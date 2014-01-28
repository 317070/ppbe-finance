from django.db import models
from finance.settings import SITE_ROOT
import re
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import datetime, timedelta, now
from smtplib import SMTPRecipientsRefused
import date

class Person(models.Model):
    name = models.CharField(max_length=127)
    street = models.CharField(max_length=127,blank=True)
    number = models.IntegerField(blank=True)
    bus = models.CharField(max_length=127,blank=True)
    postal_code = models.IntegerField(blank=True)
    city = models.CharField(max_length=127,blank=True)
    banking_account = models.ManyToManyField('Banking_Account',related_name="owner")
    current_banking_account = models.ForeignKey('Banking_Account')
    
    notas = models.CharField(max_length=127,blank=True)
    
    custom_payment_date = models.DateField(blank=True, null=True)
    email_address = models.EmailField(blank=True)
    is_member = models.BooleanField(default=True)
    email_reminder = models.BooleanField(default=True)
    email_reminder_count = models.IntegerField(default=0)
    coreteam_warned = models.BooleanField(default=False)

    @property
    def address(self):
        return "%s\n%s %s(%s)\n%s %s"%(self.name, self.street, self.number, self.bus, self.postal_code, self.city)

    @property
    def last_payment_date(self):
        try:
            d1 = self.transactions.latest('date').date
        except:
            d1 = None
        d2 = self.custom_payment_date
        if d1 and d2:
            if d2 < d1:
                return d1
            if d1 < d2:
                return d2
        elif d1:
            return d1
        elif d2:
            return d2
        else:
            return None
    

    def __str__(self):
        return self.name

    def warn_coreteam(self):
        if self.coreteam_warned:
            return False 
        text = render_to_string('mails/coreteam_contact.txt', dictionary={'name':self.name, 'address':self.address, 'email':self.email_address})
        try:
            #pass
            send_mail('Finance Squad', text, self.email_address, ["coreteam@pirateparty.be"], fail_silently=False)
            self.coreteam_warned = True
            self.save()
            return True
        except SMTPRecipientsRefused:
            print "refused"
            return False

    def send_reminder_mail(self):
        if not self.email_reminder:
            return False
        if self.last_payment_date > date.today()-timedelta(days=366):
            return False
        if self.last_payment_date > date.today()-timedelta(days=366+1*30) and email_reminder_count>=1:
            return False
        if self.last_payment_date > date.today()-timedelta(days=366+2*30) and email_reminder_count>=2:
            return False
        if email_reminder_count >= 3: #don't send more than 3 mails
            return False
        text = render_to_string('mails/reminder.txt', dictionary={})
        try:
            #pass
            send_mail('Finance Squad', text, settings.DEFAULT_FROM_EMAIL, [self.email_address], fail_silently=False)
            self.email_reminder_count += 1
            self.save()
            return True
        except SMTPRecipientsRefused:
            print "refused"
            return False


class Banking_Account(models.Model):
    iban = models.CharField(max_length=127)

    def __str__(self):
        return ' '.join(self.iban[i:i+4] for i in xrange(0, len(self.iban), 4))
        
    @staticmethod
    def clean(value):
        value = value.replace(" ", "")
        if Banking_Account.isBBAN(value):
            try:
                value = Banking_Account.convertBBANToIBAN(value)
            except:
                raise NameError('"%s" is neither BBAN nor IBAN' % value)
        if Banking_Account.isIBAN(value):
            return value
        else:
            raise NameError('"%s" is neither BBAN nor IBAN' % value)
    
    @staticmethod
    def convertBBANToIBAN(bban):
        """Calculate 2-digit checksum of an IBAN."""
        code     = "BE"
        bban     = bban.replace("-", "")
    
        # Assemble digit string
        digits = ""
        for ch in bban.upper():
            if ch.isdigit():
                digits += ch
            else:
                digits += str(ord(ch) - ord("A") + 10)
        for ch in code:
            digits += str(ord(ch) - ord("A") + 10)
        digits += "00"
        # Calculate checksum
        checksum = 98 - (long(digits) % 97)
        checksum = ("%d"%(100+checksum))[1:3]
        IBAN = "%s%s%s"%(code,checksum,bban)
        return IBAN

    @staticmethod
    def isBBAN(bban):
        r = re.compile('^\d{3}-\d{7}-\d{2}$')
        if r.match(bban) is not None:
            return True
        return False

    @staticmethod
    def isIBAN(iban):
        r = re.compile('^\w{2}[\d\w]*$')
        if r.match(iban) is not None:
            return True
        return False

class Pirate_Account(models.Model):
    name = models.CharField(default="Rekening",max_length=127)
    account = models.ForeignKey('Banking_Account')

    def __str__(self):
        return self.name + " (%s)"%self.account
    
class Transaction(models.Model):

    date = models.DateField()
    pirate_account = models.ForeignKey('Pirate_Account')
    
    amount = models.FloatField()
    BIC = models.CharField(max_length=127,blank=True)
    code = models.CharField(max_length=127,blank=True)
    statement = models.TextField(blank=True)
    
    beneficiary = models.ForeignKey(Person, related_name="transactions")
    public = models.BooleanField(default=False)

    thankyou_sent = models.BooleanField(default=False)

    def send_thankyou_mail(self):
        if self.thankyou_sent:
            return False
        if self.amount<0.0:
            return False
        text = render_to_string('mails/thankyou.txt', dictionary={})
        try:
            #pass
            send_mail('Finance Squad', text, settings.DEFAULT_FROM_EMAIL, [self.beneficiary.email_address], fail_silently=False)
            self.thankyou_sent = True
            self.save()
            return True
        except SMTPRecipientsRefused:
            print "refused"
            return False            

class Payment(models.Model):
    amount = models.FloatField()
    code = models.CharField(max_length=127,blank=True)
    payer = models.ForeignKey(Person, related_name="payments")
    mail_to = models.ManyToManyField(Person, related_name="following_payments",blank=True)
    
class Reimbursement(models.Model):
    amount = models.FloatField()
    statement = models.TextField(blank=True)
    beneficiary = models.ForeignKey(Person, related_name="reimbursements")
    mail_to = models.ForeignKey(Person, related_name="following_reimbursements",blank=True)
    proof = models.FileField(upload_to=SITE_ROOT+"/uploads",blank=True)
