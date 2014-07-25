from django.contrib import admin
from finance.models import Person, Transaction, Pirate_Account
from finance import views
from django.core import urlresolvers
import sys
from django.utils.timezone import datetime, timedelta, now
from datetime import date

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
        if obj.beneficiary.firstname in obj.statement.upper():
            return
        if obj.beneficiary.lastname in obj.statement.upper():
            return
    queryset.update(public=True)
make_public.short_description = "Make public"

def warn_coreteam(modeladmin, request, queryset):
    for obj in queryset:
        obj.warn_coreteam()
warn_coreteam.short_description = "Warn coreteam"

def send_reminder_mail(modeladmin, request, queryset):
    for obj in queryset:
        obj.send_reminder_mail()
send_reminder_mail.short_description = "Send a reminder mail"

def send_thankyou_mail(modeladmin, request, queryset):
    for obj in queryset:
        obj.send_thankyou_mail()
send_thankyou_mail.short_description = "Send a thanking mail"


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'beneficiary','email',  'public', 'statement',)
    date_hierarchy = 'date'
    fieldsets = (
        (None, {
            'fields': ('beneficiary','beneficiary_admin_link','amount','date', 'public', 'statement', )
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('BIC', 'code', 'pirate_account','thankyou_sent')
        }),
    )
    readonly_fields = ('email','beneficiary_admin_link')
    actions = [make_public, send_thankyou_mail]
    
    def email(self, transaction):
        return transaction.beneficiary.email_address

    def beneficiary_admin_link(self, transaction):
        return '<a href="%s">%s %s(%s)</a>' % (urlresolvers.reverse('admin:finance_person_change', args=(transaction.beneficiary.id,)), transaction.beneficiary.firstname, transaction.beneficiary.lastname, transaction.beneficiary.email_address)
    
    beneficiary_admin_link.allow_tags = True
    beneficiary_admin_link.short_description = 'Beneficiary'
    
class PersonAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'is_valid_member', 'doesnt_have_nonpublic_payments', 'email_address', 'last_payment', 'email_reminder_count', 'coreteam_warned', 'current_banking_account','street','postal_code','city','language')
    inlines = [TransactionInline]
    fieldsets = (
        (None, {
            'fields': ('is_member', 'firstname', 'lastname', 'street', 'postal_code', 'city', 'email_address', 'telephone', 'custom_payment_date', 'current_banking_account','language')
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('email_reminder', 'email_reminder_count', 'banking_account', 'coreteam_warned','notas')
        }),
    )
    actions = [warn_coreteam, send_reminder_mail]
    readonly_fields = ('last_payment','doesnt_have_nonpublic_payments','is_valid_member')
    
    def last_payment(self, person):
        return person.last_payment_date
    
    def doesnt_have_nonpublic_payments(self, person):
        return not person.transactions.filter(public=False).exists()
    doesnt_have_nonpublic_payments.boolean = True
    doesnt_have_nonpublic_payments.short_description = 'No secret transactions'
    
    def is_valid_member(self, person):
        return person.is_valid_member
    is_valid_member.boolean = True
    
    last_payment.admin_order_field = 'transactions__date'

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Pirate_Account, PirateAccountAdmin)
