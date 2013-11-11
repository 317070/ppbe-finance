from django.test import TestCase
from finance.models import Banking_Account

class IBANTestCase(TestCase):
    def setUp(self):
        pass
        
    def test_iban_converter(self):
        """Animals that can speak are correctly identified"""
        self.assertEqual(Banking_Account.convertBBANToIBAN("091-0002777-90"), 'BE34091000277790')
        self.assertEqual(Banking_Account.convertBBANToIBAN("679-2005502-27"), 'BE48679200550227')
        self.assertEqual(Banking_Account.isBBAN("679-2005502-27"), True)
        self.assertEqual(Banking_Account.isBBAN('BE48679200550227'), False)
        self.assertEqual(Banking_Account.isIBAN("679-2005502-27"), False)
        self.assertEqual(Banking_Account.isIBAN('BE48679200550227'), True)
        