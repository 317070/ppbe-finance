from django.contrib import admin
from finance.models import Person, Transaction, Pirate_Account
from finance import views
from django.core import urlresolvers
import sys

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    can_delete = False

class PersonInline(admin.TabularInline):
    model = Person
    extra = 0
    can_delete = False

class PirateAccountAdmin(admin.ModelAdmin):
    pass

def make_public(modeladmin, request, queryset):
    for obj in queryset:
        if "AT" in obj.statement.upper():
            return
    queryset.update(public=True)
make_public.short_description = "Make public"

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'beneficiary','email',  'public', 'statement',)
    date_hierarchy = 'date'
    fieldsets = (
        (None, {
            'fields': ('beneficiary','beneficiary_admin_link','amount','date', 'public', 'statement', )
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('BIC', 'code', 'pirate_account')
        }),
    )
    readonly_fields = ('email','beneficiary_admin_link')
    actions = [make_public]
    
    def email(self, transaction):
        return transaction.beneficiary.email_address

    def beneficiary_admin_link(self, transaction):
        return '<a href="%s">%s (%s)</a>' % (urlresolvers.reverse('admin:finance_person_change', args=(transaction.beneficiary.id,)), transaction.beneficiary.name, transaction.beneficiary.email_address)
    
    beneficiary_admin_link.allow_tags = True
    beneficiary_admin_link.short_description = 'Beneficiary'
    
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'doesnt_have_nonpublic_payments', 'email_address', 'last_payment', 'current_banking_account','street','number','bus','postal_code','city','notas')
    inlines = [TransactionInline]
    fieldsets = (
        (None, {
            'fields': ('is_member', 'name','street','number', 'bus', 'postal_code', 'city', 'email_address', 'current_banking_account')
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('email_reminder', 'email_reminder_count', 'banking_account','custom_payment_date')
        }),
    )
    readonly_fields = ('last_payment','doesnt_have_nonpublic_payments',)
    
    def last_payment(self, person):
        return person.last_payment_date
    
    def doesnt_have_nonpublic_payments(self, person):
        return not person.transactions.filter(public=False).exists()
    doesnt_have_nonpublic_payments.boolean = True
    doesnt_have_nonpublic_payments.short_description = 'Does not have non-public transactions'
    
    last_payment.admin_order_field = 'transactions__date'

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Pirate_Account, PirateAccountAdmin)
