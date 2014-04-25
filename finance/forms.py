from django import forms
import csv
from finance.models import Pirate_Account, Banking_Account, Person, Transaction
import re
from datetime import datetime
from email.utils import parseaddr

class CSVInputForm(forms.Form):
    file = forms.FileField()

    def save(self):
        messages = []
        success = False
        dialect = csv.excel()
        dialect.quotechar = '"'
        dialect.delimiter = ','
        
        records = csv.reader(self.cleaned_data["file"], dialect=dialect)
        for line in records:
            date = line[0]
            account = line[1]
            amount = line[2]
            beneficiary = line[3]
            BIC = line[4]
            name = line[5]
            address = line[6]
            code = line[7]
            statement = line[8]
            
            try:
                account = Banking_Account.clean(account)
            except NameError, e:
                messages.append("Error => Could not convert to IBAN. " + str(e))
                success = False
                continue
            
            if beneficiary: # payment to bank
                try:
                    beneficiary = Banking_Account.clean(beneficiary)
                except NameError, e:
                    messages.append("Error => Could not convert to IBAN. " + str(e))
                    success = False
                    continue
            
            (own_account, created) = Banking_Account.objects.get_or_create(iban=account)
            (pirate_account, created) = Pirate_Account.objects.all().get_or_create(account=own_account)
            if created:
                messages.append("The new Pirate Party account with IBAN %s was created"%account)
            
            (beneficiary_account, created) = Banking_Account.objects.get_or_create(iban=beneficiary)
            
            transaction_date = datetime.strptime(date, '%d-%m-%Y').date()
            (street, postal_code, city) = self.process_address(address)
            
            try:
                lastname = name.split(None,1)[0].title()
                firstname = name.split(None,1)[1].title()
            except:
                firstname = name
                lastname = ""
            try:
                payer = Person.objects.get(current_banking_account = beneficiary_account)
            except:
                try:
                    payer = Person.objects.get(firstname=firstname, lastname=lastname, postal_code=postal_code)                
                except:
                    try:
                        payer = Person.objects.get(firstname=lastname, lastname=firstname, postal_code=postal_code)                
                    except:
                        messages.append("The new member %s %s was created"%(firstname, lastname))
                        payer = Person()
            
            if not payer.transactions.exists() or payer.transactions.latest('date').date < transaction_date:
                # this is the most recent transaction. Update the information we have
                #payer.firstname = firstname
                #payer.lastname = lastname
                #payer.street = street
                #payer.postal_code = postal_code
                #payer.city = city
                payer.current_banking_account = beneficiary_account
                payer.email_reminder_count = 0
                    
            payer.save()
            if not beneficiary_account.owner.exists():
                payer.banking_account.add(beneficiary_account)
            payer.save()
            
            amount = float(amount.replace(".","").replace(",","."))
            
            (transaction, created) = Transaction.objects.get_or_create(
                                            date=transaction_date, 
                                            beneficiary=payer, 
                                            amount=amount,
                                            pirate_account=pirate_account)
            transaction.BIC = BIC
            transaction.code = code
            transaction.statement = statement
            transaction.public = False
            transaction.save()
            
        return (success, messages)
    
    @staticmethod
    def process_address(address):
        pattern = r'^.* \d{4}'
        match = re.findall(pattern,address[::-1])
        if not match:
            street = address
            postal_code = ''
            city = ''
        else:
            match = match[0][::-1]
            firstline = address.replace(match,"").strip()
            secondline = match.strip()
            street = firstline
            
            postal_code = re.findall(r"\d{4}",secondline)[0]
            city = secondline.replace(postal_code,"").strip()
            postal_code = int(postal_code)
        
        if postal_code == "":
            postal_code = 0
        return (street, postal_code, city)
