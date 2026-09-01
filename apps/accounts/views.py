from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import CustomUser
from .forms import LoginForm, OfficerCreationForm, UserProfileForm
from .decorators import admin_required
from apps.members.forms import MemberSelfRegistrationForm
from apps.members.models import MemberProfile
from apps.savings.models import SavingsAccount
from apps.notifications.utils import notify_user, notify_staff_and_admins

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = MemberSelfRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                # 1. Create User as inactive until approved by officer
                user = CustomUser.objects.create_user(
                    username=form.cleaned_data['username'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data.get('email', ''),
                    phone=form.cleaned_data.get('phone', ''),
                    role='MEMBER',
                    password=form.cleaned_data['password'],
                    is_active=False
                )

                # 2. Attach Profile Picture to User if provided
                if 'member_photo' in request.FILES:
                    user.profile_picture = request.FILES['member_photo']
                    user.save(update_fields=['profile_picture'])

                # 3. Create Member Profile with PENDING status
                profile = form.save(commit=False)
                profile.user = user
                profile.status = 'PENDING'
                profile.save()

                # 4. Provision initial Savings Account
                SavingsAccount.objects.create(
                    member=profile,
                    account_number=f"SAV-{profile.member_id.replace('TNS-MEM-', '')}"
                )

                # 5. Notify Field Officers & Admins for KYC Review
                notify_staff_and_admins(
                    title="New Member Application Pending Approval",
                    message=f"Member {profile.member_id} ({user.get_full_name()}) submitted an application with KYC photos. Officer review & approval required.",
                    link=f"/members/{profile.id}/",
                    notification_type='INFO'
                )

                # 6. Save registration info in session for greeting confirmation
                request.session['registration_info'] = {
                    'name': user.get_full_name() or user.username,
                    'member_id': profile.member_id,
                    'username': user.username,
                    'phone': user.phone or 'N/A'
                }
                return redirect('accounts:registration_submitted')
        else:
            messages.error(request, "Please correct the errors below in the registration form.")
    else:
        form = MemberSelfRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def registration_submitted_view(request):
    registration_info = request.session.get('registration_info', {
        'name': 'Valued Member',
        'member_id': 'TNS-MEM-PENDING',
        'username': 'Your account',
        'phone': ''
    })
    return render(request, 'accounts/registration_submitted.html', {
        'info': registration_info
    })

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})

@admin_required
def officer_list_view(request):
    officers = CustomUser.objects.filter(role='OFFICER').order_by('-date_joined')
    form = OfficerCreationForm()
    
    if request.method == 'POST':
        form = OfficerCreationForm(request.POST)
        if form.is_valid():
            officer = form.save()
            messages.success(request, f"Officer account for '{officer.username}' created successfully.")
            return redirect('accounts:officer_list')
        else:
            messages.error(request, "Please fix the errors in the form.")

    from django.core.paginator import Paginator
    paginator = Paginator(officers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/officer_list.html', {
        'page_obj': page_obj,
        'officers': page_obj,
        'form': form,
    })

@admin_required
def officer_toggle_status(request, user_id):
    officer = get_object_or_404(CustomUser, id=user_id, role='OFFICER')
    officer.is_active = not officer.is_active
    officer.save()
    status_text = "activated" if officer.is_active else "deactivated"
    messages.success(request, f"Officer {officer.username} has been {status_text}.")
    return redirect('accounts:officer_list')
