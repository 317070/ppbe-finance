from django.db import models
from finance.settings import SITE_ROOT
import re

class Person(models.Model):
    name = models.CharField(max_length=127)
    street = models.CharField(max_length=127)
    number = models.IntegerField()
    bus = models.CharField(max_length=127)
    postal_code = models.IntegerField()
    city = models.CharField(max_length=127)
    banking_account = models.ManyToManyField('Banking_Account',related_name="owner")
    current_banking_account = models.ForeignKey('Banking_Account')
    
    email_address = models.EmailField()
    is_member = models.BooleanField(default=True)
    email_reminder = models.BooleanField(default=True)
    email_reminder_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

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
    BIC = models.CharField(max_length=127)
    code = models.CharField(max_length=127)
    statement = models.TextField()
    
    beneficiary = models.ForeignKey(Person, related_name="transactions")
    

class Payment(models.Model):
    amount = models.FloatField()
    code = models.CharField(max_length=127)
    payer = models.ForeignKey(Person, related_name="payments")
    mail_to = models.ManyToManyField(Person, related_name="following_payments")
    
class Reimbursement(models.Model):
    amount = models.FloatField()
    statement = models.TextField()
    beneficiary = models.ForeignKey(Person, related_name="reimbursements")
    mail_to = models.ForeignKey(Person, related_name="following_reimbursements")
    proof = models.FileField(upload_to=SITE_ROOT+"/uploads")


