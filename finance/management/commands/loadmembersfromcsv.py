import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import random
import datetime, csv
from finance.models import Person

class Command(BaseCommand):
    args = '<path to the csv-file> [<group name>]'
    help = '''Arguments:
                  - path to the csv-file
           '''

    def handle(self, *args, **options):
        ## parse arguments
        # get arguments
        assert 1 == len(args), "One argument required for this command"
        filepath = args[0]
        
        # check filepath
        assert os.path.exists(filepath), "csv-file not found"
        # parse file
        with open(filepath) as f:
            reader = csv.reader(f,delimiter=';')
            for row in reader:
                if not row[6]:
                    row[6] = 0
                _, created = Person.objects.get_or_create(
                    lastname = row[1],
                    firstname = row[2],
                    email_address = row[3],
                    language = row[4],
                    street = row[5],
                    postal_code = row[6],
                    city = row[7],
                    custom_payment_date = datetime.datetime.strptime(row[8], '%Y-%m-%d'),
                    telephone = row[9]
                    )
                # creates a tuple of the new object or
                # current object and a boolean of if it was created
                if created:
                    self.stdout.write("Imported %s %s\n"%(row[2],row[1]))
                else:
                    self.stdout.write("-> Duplicate: %s %s\n"%(row[2],row[1]))
        self.stdout.write("Done\n\n")
        
        pass
            