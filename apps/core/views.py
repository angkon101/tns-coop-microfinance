from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.core.pdf_service import generate_daily_sheet_pdf
from apps.accounts.models import CustomUser
from apps.accounts.decorators import admin_required, officer_required, member_required
from apps.members.models import MemberProfile
from apps.savings.models import SavingsAccount, SavingsTransaction
from apps.loans.models import LoanApplication, LoanInstallment

def dashboard_dispatcher(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.user.is_admin_user or request.user.is_superuser:
        return redirect('core:admin_dashboard')
    elif request.user.is_officer_user:
        return redirect('core:officer_dashboard')
    else:
        return redirect('core:member_dashboard')

# ----------------- MEMBER DASHBOARD ----------------- #

@member_required
def member_dashboard(request):
    profile = getattr(request.user, 'member_profile', None)
    if not profile:
        # If member profile doesn't exist yet, auto-create one
        profile, _ = MemberProfile.objects.get_or_create(user=request.user)

    account, _ = SavingsAccount.objects.get_or_create(
        member=profile,
        defaults={'account_number': f"SAV-{profile.member_id.replace('TNS-MEM-', '')}"}
    )

    # Active loans
    active_loans = profile.loans.filter(status='DISBURSED')
    total_loan_outstanding = sum(loan.remaining_balance for loan in active_loans)

    # Next upcoming installment
    next_installment = LoanInstallment.objects.filter(
        loan__member=profile,
        status='PENDING'
    ).order_by('due_date').first()

    # Recent transactions
    recent_transactions = account.transactions.all().order_by('-created_at')[:5]

    # Recent loans
    recent_loans = profile.loans.all().order_by('-applied_at')[:5]

    return render(request, 'dashboard/member_dashboard.html', {
        'profile': profile,
        'account': account,
        'active_loans': active_loans,
        'total_loan_outstanding': total_loan_outstanding,
        'next_installment': next_installment,
        'recent_transactions': recent_transactions,
        'recent_loans': recent_loans,
    })

# ----------------- OFFICER DASHBOARD ----------------- #

@officer_required
def officer_dashboard(request):
    today = timezone.now().date()

    # Member Stats
    total_members = MemberProfile.objects.count()
    active_members = MemberProfile.objects.filter(status='ACTIVE').count()
    pending_members_count = MemberProfile.objects.filter(status='PENDING').count()
    pending_members = MemberProfile.objects.filter(status='PENDING').select_related('user').order_by('-created_at')[:5]

    # Savings requests
    pending_savings_count = SavingsTransaction.objects.filter(status='PENDING').count()
    today_deposit_collected = SavingsTransaction.objects.filter(
        transaction_type='DEPOSIT',
        status='APPROVED',
        created_at__date=today
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Loan Stats
    pending_loans_count = LoanApplication.objects.filter(status='PENDING').count()
    active_loans_count = LoanApplication.objects.filter(status='DISBURSED').count()
    
    today_installment_collected = LoanInstallment.objects.filter(
        status='PAID',
        paid_date=today
    ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')

    # Today's due installments
    today_due_installments = LoanInstallment.objects.filter(
        due_date=today,
        status='PENDING'
    ).select_related('loan__member__user')[:10]

    # Overdue installments
    overdue_installments = LoanInstallment.objects.filter(
        due_date__lt=today,
        status='PENDING'
    ).select_related('loan__member__user').order_by('due_date')[:10]

    # Pending actions queue
    pending_deposits = SavingsTransaction.objects.filter(
        status='PENDING'
    ).select_related('account__member__user')[:5]

    pending_loans = LoanApplication.objects.filter(
        status='PENDING'
    ).select_related('member__user')[:5]

    return render(request, 'dashboard/officer_dashboard.html', {
        'total_members': total_members,
        'active_members': active_members,
        'pending_members_count': pending_members_count,
        'pending_members': pending_members,
        'pending_savings_count': pending_savings_count,
        'pending_loans_count': pending_loans_count,
        'active_loans_count': active_loans_count,
        'today_deposit_collected': today_deposit_collected,
        'today_installment_collected': today_installment_collected,
        'today_total_collection': today_deposit_collected + today_installment_collected,
        'today_due_installments': today_due_installments,
        'overdue_installments': overdue_installments,
        'pending_deposits': pending_deposits,
        'pending_loans': pending_loans,
    })

# ----------------- ADMIN DASHBOARD ----------------- #

@admin_required
def admin_dashboard(request):
    today = timezone.now().date()

    # User & Member counts
    total_officers = CustomUser.objects.filter(role='OFFICER').count()
    total_members = MemberProfile.objects.count()

    # Savings Aggregates
    total_savings_balance = SavingsAccount.objects.aggregate(Sum('balance'))['balance__sum'] or Decimal('0.00')
    total_deposit_sum = SavingsTransaction.objects.filter(
        transaction_type='DEPOSIT', status='APPROVED'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_withdrawal_sum = SavingsTransaction.objects.filter(
        transaction_type='WITHDRAWAL', status='APPROVED'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Loan Aggregates
    total_loans_disbursed_count = LoanApplication.objects.filter(status__in=['DISBURSED', 'COMPLETED']).count()
    total_disbursed_amount = LoanApplication.objects.filter(
        status__in=['DISBURSED', 'COMPLETED']
    ).aggregate(Sum('principal_amount'))['principal_amount__sum'] or Decimal('0.00')

    total_expected_payable = LoanApplication.objects.filter(
        status__in=['DISBURSED', 'COMPLETED']
    ).aggregate(Sum('total_payable'))['total_payable__sum'] or Decimal('0.00')

    total_loan_repaid = LoanApplication.objects.filter(
        status__in=['DISBURSED', 'COMPLETED']
    ).aggregate(Sum('total_paid'))['total_paid__sum'] or Decimal('0.00')

    total_loan_outstanding = max(Decimal('0.00'), total_expected_payable - total_loan_repaid)
    total_profit_interest_earned = LoanApplication.objects.filter(
        status__in=['DISBURSED', 'COMPLETED']
    ).aggregate(Sum('total_interest'))['total_interest__sum'] or Decimal('0.00')

    # Status counts
    pending_loans_count = LoanApplication.objects.filter(status='PENDING').count()
    pending_savings_count = SavingsTransaction.objects.filter(status='PENDING').count()
    pending_members_count = MemberProfile.objects.filter(status='PENDING').count()

    # Recent system activities
    recent_transactions = SavingsTransaction.objects.select_related(
        'account__member__user', 'created_by'
    ).order_by('-created_at')[:8]

    recent_loans = LoanApplication.objects.select_related(
        'member__user'
    ).order_by('-applied_at')[:8]

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_officers': total_officers,
        'total_members': total_members,
        'total_savings_balance': total_savings_balance,
        'total_deposit_sum': total_deposit_sum,
        'total_withdrawal_sum': total_withdrawal_sum,
        'total_loans_disbursed_count': total_loans_disbursed_count,
        'total_disbursed_amount': total_disbursed_amount,
        'total_loan_repaid': total_loan_repaid,
        'total_loan_outstanding': total_loan_outstanding,
        'total_profit_interest_earned': total_profit_interest_earned,
        'pending_loans_count': pending_loans_count,
        'pending_savings_count': pending_savings_count,
        'pending_members_count': pending_members_count,
        'recent_transactions': recent_transactions,
        'recent_loans': recent_loans,
    })

# ----------------- DAILY COLLECTION SHEET GENERATOR ----------------- #

from datetime import datetime

@officer_required
def collection_sheet_view(request):
    today = timezone.now().date()
    date_str = request.GET.get('date', '')
    officer_id = request.GET.get('officer', '')

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else today
    except ValueError:
        selected_date = today

    all_officers = CustomUser.objects.filter(role='OFFICER').order_by('first_name')

    # Base query for members
    members_qs = MemberProfile.objects.filter(status='ACTIVE').select_related('user', 'savings_account', 'assigned_officer').prefetch_related('loans__installments').order_by('member_id')

    if officer_id:
        members_qs = members_qs.filter(assigned_officer_id=officer_id)

    # Today's Savings Deposits Collection
    deposits_qs = SavingsTransaction.objects.filter(
        transaction_type='DEPOSIT',
        status='APPROVED',
        created_at__date=selected_date
    ).select_related('account__member__user', 'created_by')

    if officer_id:
        deposits_qs = deposits_qs.filter(account__member__assigned_officer_id=officer_id)

    total_deposit_collection = deposits_qs.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Today's Loan Installment Collections
    installments_paid_qs = LoanInstallment.objects.filter(
        status='PAID',
        paid_date=selected_date
    ).select_related('loan__member__user', 'collected_by')

    if officer_id:
        installments_paid_qs = installments_paid_qs.filter(loan__member__assigned_officer_id=officer_id)

    total_installment_collection = installments_paid_qs.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')

    # Payment Methods breakdown
    cash_deposits = deposits_qs.filter(payment_method='CASH').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    digital_deposits = deposits_qs.filter(payment_method__in=['BKASH', 'NAGAD', 'BANK']).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Due Installments for the selected date
    due_installments_qs = LoanInstallment.objects.filter(
        due_date=selected_date,
        status__in=['PENDING', 'OVERDUE']
    ).select_related('loan__member__user')

    if officer_id:
        due_installments_qs = due_installments_qs.filter(loan__member__assigned_officer_id=officer_id)

    expected_installment_amount = due_installments_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')

    grand_total_collected = total_deposit_collection + total_installment_collection

    if request.GET.get('format') == 'pdf' or request.GET.get('export') == 'pdf':
        pdf_bytes = generate_daily_sheet_pdf(
            selected_date=selected_date,
            deposits=deposits_qs,
            installments_paid=installments_paid_qs,
            due_installments=due_installments_qs,
            grand_total=grand_total_collected,
            total_deposit=total_deposit_collection,
            total_installment=total_installment_collection,
            cash_deposits=cash_deposits,
            digital_deposits=digital_deposits,
            members=members_qs
        )
        filename = f"Daily_Collection_Sheet_{selected_date.strftime('%Y%m%d')}.pdf"
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response

    return render(request, 'dashboard/collection_sheet.html', {
        'members': members_qs,
        'selected_date': selected_date,
        'all_officers': all_officers,
        'selected_officer_id': officer_id,
        'deposits': deposits_qs,
        'installments_paid': installments_paid_qs,
        'due_installments': due_installments_qs,
        'total_deposit_collection': total_deposit_collection,
        'total_installment_collection': total_installment_collection,
        'grand_total_collected': grand_total_collected,
        'cash_deposits': cash_deposits,
        'digital_deposits': digital_deposits,
        'expected_installment_amount': expected_installment_amount,
        'generated_at': timezone.now(),
    })

# ----------------- FINANCIAL REPORTS ----------------- #

@admin_required
def financial_reports_view(request):
    # Summary of Inflow vs Outflow
    total_deposits = SavingsTransaction.objects.filter(transaction_type='DEPOSIT', status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_withdrawals = SavingsTransaction.objects.filter(transaction_type='WITHDRAWAL', status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_loans_given = LoanApplication.objects.filter(status__in=['DISBURSED', 'COMPLETED']).aggregate(Sum('principal_amount'))['principal_amount__sum'] or Decimal('0.00')
    total_repayments_collected = LoanApplication.objects.aggregate(Sum('total_paid'))['total_paid__sum'] or Decimal('0.00')

    net_cash_inflow = (total_deposits + total_repayments_collected) - (total_withdrawals + total_loans_given)

    # All Completed Transactions
    recent_transactions = SavingsTransaction.objects.filter(status='APPROVED').select_related('account__member__user').order_by('-processed_at')[:25]
    all_loans = LoanApplication.objects.filter(status__in=['DISBURSED', 'COMPLETED']).select_related('member__user').order_by('-disbursed_at')[:25]

    return render(request, 'dashboard/financial_reports.html', {
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_loans_given': total_loans_given,
        'total_repayments_collected': total_repayments_collected,
        'net_cash_inflow': net_cash_inflow,
        'recent_transactions': recent_transactions,
        'all_loans': all_loans,
    })
