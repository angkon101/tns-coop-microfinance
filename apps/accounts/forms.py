from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from django.db.models import Q

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email', 'id': 'username_input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'id': 'password_input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user_obj = CustomUser.objects.filter(Q(username=username) | Q(email=username)).first()
            if user_obj and user_obj.check_password(password):
                # Check member KYC review status if member
                if hasattr(user_obj, 'member_profile'):
                    profile = user_obj.member_profile
                    if profile.status == 'PENDING' or not user_obj.is_active:
                        raise forms.ValidationError(
                            f"⏳ Account ({profile.member_id}) is pending KYC verification and officer approval. You will be able to log in as soon as an officer approves your registration."
                        )
                    elif profile.status == 'REJECTED':
                        reason_msg = f" Reason: {profile.rejection_reason}" if profile.rejection_reason else ""
                        raise forms.ValidationError(
                            f"❌ Your membership application was rejected by the officer.{reason_msg} Please contact Touch & Solve office."
                        )
                    elif profile.status == 'INACTIVE' or not user_obj.is_active:
                        raise forms.ValidationError("This member account has been deactivated. Please contact your field officer.")
                elif not user_obj.is_active:
                    raise forms.ValidationError("This account has been deactivated.")

                cleaned_data['user'] = user_obj
            else:
                raise forms.ValidationError("Invalid username/email or password.")
        return cleaned_data

class OfficerCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'OFFICER'
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
