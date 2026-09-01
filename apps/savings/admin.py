from django.contrib import admin
from .models import SavingsAccount, SavingsTransaction

@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'member', 'balance', 'updated_at')
    search_fields = ('account_number', 'member__member_id', 'member__user__first_name', 'member__user__last_name')

@admin.register(SavingsTransaction)
class SavingsTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'transaction_type', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'payment_method', 'created_at')
    search_fields = ('account__account_number', 'account__member__member_id', 'reference_note')
