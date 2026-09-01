from django import forms
from apps.accounts.models import CustomUser
from .models import MemberProfile

class MemberSelfRegistrationForm(forms.ModelForm):
    # Personal & Account
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose Username'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address (optional)'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password (min. 6 characters)'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    # Address & NID
    present_address = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Current living address'}))
    permanent_address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Village/Town, Post, Upazila, District'}))
    nid_number = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID (NID) Number'}))
    occupation = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation (optional)'}))
    gender = forms.ChoiceField(choices=MemberProfile.GENDER_CHOICES, required=False, initial='MALE', widget=forms.Select(attrs={'class': 'form-select'}))

    # Photos
    member_photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    nid_photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    nominee_photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    # Nominee Details
    nominee_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nominee Full Name'}))
    nominee_relation = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Relationship with Member'}))
    nominee_phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nominee Phone Number'}))
    nominee_nid = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nominee NID (optional)'}))

    class Meta:
        model = MemberProfile
        fields = [
            'nid_number', 'gender', 'present_address', 'permanent_address', 'occupation',
            'member_photo', 'nid_photo',
            'nominee_name', 'nominee_relation', 'nominee_phone', 'nominee_nid', 'nominee_photo'
        ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please re-enter carefully.")
        return cleaned_data


class MemberRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address (optional)'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Initial Password'}), initial='123456')

    class Meta:
        model = MemberProfile
        fields = [
            'nid_number', 'gender', 'date_of_birth', 'father_or_husband_name', 'mother_name',
            'occupation', 'present_address', 'permanent_address',
            'member_photo', 'nid_photo',
            'nominee_name', 'nominee_relation', 'nominee_nid', 'nominee_phone', 'nominee_photo',
            'assigned_officer', 'status'
        ]
        widgets = {
            'nid_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID / Smart Card'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'father_or_husband_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'present_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'member_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'nid_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'nominee_name': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_relation': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_nid': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'assigned_officer': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username


class MemberProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = MemberProfile
        fields = [
            'nid_number', 'gender', 'date_of_birth', 'father_or_husband_name', 'mother_name',
            'occupation', 'present_address', 'permanent_address',
            'member_photo', 'nid_photo',
            'nominee_name', 'nominee_relation', 'nominee_nid', 'nominee_phone', 'nominee_photo',
            'assigned_officer', 'status'
        ]
        widgets = {
            'nid_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'father_or_husband_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'present_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'member_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'nid_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'nominee_name': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_relation': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_nid': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'assigned_officer': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
