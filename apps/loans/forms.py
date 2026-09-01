from django import forms
from decimal import Decimal
from .models import LoanApplication, LoanScheme, LoanInstallment
from apps.members.models import MemberProfile

class MemberLoanApplicationForm(forms.ModelForm):
    loan_product = forms.ModelChoiceField(
        queryset=LoanScheme.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'loan_product_select'}),
        empty_label="-- Select Loan Scheme (Optional) --"
    )
    principal_amount = forms.DecimalField(
        min_value=Decimal('1000.00'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Loan Amount in BDT'})
    )
    duration_months = forms.IntegerField(
        min_value=1,
        max_value=60,
        initial=12,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration (Months)'})
    )
    installment_frequency = forms.ChoiceField(
        choices=LoanApplication.FREQUENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    purpose = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Small Grocery Store expansion, Agriculture'})
    )
    guarantor_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guarantor Full Name'})
    )
    guarantor_phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guarantor Phone Number'})
    )
    guarantor_nid = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guarantor NID / Smart Card'})
    )
    guarantor_relation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Brother, Neighbor, Business Partner'})
    )

    class Meta:
        model = LoanApplication
        fields = [
            'loan_product', 'principal_amount', 'duration_months', 'installment_frequency',
            'purpose', 'guarantor_name', 'guarantor_phone', 'guarantor_nid', 'guarantor_relation'
        ]

class StaffLoanApplicationForm(MemberLoanApplicationForm):
    member = forms.ModelChoiceField(
        queryset=MemberProfile.objects.filter(status='ACTIVE').select_related('user'),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        empty_label="-- Select Member --"
    )

    class Meta(MemberLoanApplicationForm.Meta):
        fields = ['member'] + MemberLoanApplicationForm.Meta.fields

class LoanSchemeForm(forms.ModelForm):
    class Meta:
        model = LoanScheme
        fields = ['name', 'min_amount', 'max_amount', 'interest_rate_percent', 'duration_months', 'installment_frequency', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'min_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'duration_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'installment_frequency': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
