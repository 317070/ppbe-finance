from django.contrib import admin
from finance.models import Person, Transaction, Pirate_Account
from finance import views

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

class TransationAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'beneficiary')
    date_hierarchy = 'date'
    fieldsets = (
        (None, {
            'fields': ('beneficiary','amount','date', 'statement', )
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('BIC', 'code', 'pirate_account')
        }),
    )
    
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_address', 'current_banking_account','street','number','bus','postal_code','city')
    inlines = [TransactionInline]
    fieldsets = (
        (None, {
            'fields': ('is_member', 'name','street','number', 'bus', 'postal_code', 'city', 'email_address', 'current_banking_account')
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('email_reminder', 'email_reminder_count', 'banking_account')
        }),
    )
    
admin.site.register(Transaction, TransationAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Pirate_Account, PirateAccountAdmin)
