from django.contrib import admin
from .models import LoanScheme, LoanApplication, LoanInstallment

@admin.register(LoanScheme)
class LoanSchemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate_percent', 'duration_months', 'installment_frequency', 'is_active')

class LoanInstallmentInline(admin.TabularInline):
    model = LoanInstallment
    extra = 0
    readonly_fields = ('installment_number', 'due_date', 'total_amount', 'paid_amount', 'status', 'paid_date', 'collected_by')

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'member', 'principal_amount', 'interest_rate', 'total_payable', 'total_paid', 'status', 'applied_at')
    list_filter = ('status', 'installment_frequency', 'applied_at')
    search_fields = ('loan_id', 'member__member_id', 'member__user__first_name', 'member__user__last_name', 'purpose')
    inlines = [LoanInstallmentInline]

@admin.register(LoanInstallment)
class LoanInstallmentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'installment_number', 'due_date', 'total_amount', 'paid_amount', 'status', 'paid_date')
    list_filter = ('status', 'due_date')
    search_fields = ('loan__loan_id', 'loan__member__member_id')
