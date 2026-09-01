from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction

from apps.accounts.models import CustomUser
from apps.accounts.decorators import officer_required
from apps.notifications.utils import notify_user, notify_staff_and_admins
from .models import MemberProfile
from .forms import MemberRegistrationForm, MemberProfileEditForm

from django.core.paginator import Paginator

@officer_required
def member_list_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    members = MemberProfile.objects.select_related('user', 'assigned_officer').order_by('-joined_date')

    if query:
        terms = query.split()
        q_obj = Q()
        for term in terms:
            q_obj &= (
                Q(member_id__icontains=term) |
                Q(user__first_name__icontains=term) |
                Q(user__last_name__icontains=term) |
                Q(user__phone__icontains=term) |
                Q(user__username__icontains=term) |
                Q(nid_number__icontains=term)
            )
        members = members.filter(q_obj)

    if status_filter:
        members = members.filter(status=status_filter)

    paginator = Paginator(members, 10) # 10 members per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'members/member_list.html', {
        'page_obj': page_obj,
        'members': page_obj,
        'query': query,
        'status_filter': status_filter,
    })

@officer_required
def member_create_view(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                # Create CustomUser
                user = CustomUser.objects.create_user(
                    username=form.cleaned_data['username'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data.get('email', ''),
                    phone=form.cleaned_data.get('phone', ''),
                    role='MEMBER',
                    password=form.cleaned_data['password']
                )

                if 'member_photo' in request.FILES:
                    user.profile_picture = request.FILES['member_photo']
                    user.save(update_fields=['profile_picture'])

                # Create MemberProfile
                profile = form.save(commit=False)
                profile.user = user
                if not profile.assigned_officer and request.user.role == 'OFFICER':
                    profile.assigned_officer = request.user
                profile.save()

                # Automatically create default Savings Account
                from apps.savings.models import SavingsAccount
                SavingsAccount.objects.create(
                    member=profile,
                    account_number=f"SAV-{profile.member_id.replace('TNS-MEM-', '')}"
                )

                # Send welcome notification to member
                notify_user(
                    user=user,
                    title="Welcome to Touch and Solve Co-operative!",
                    message=f"Your membership ID is {profile.member_id}. Your savings account has been opened.",
                    link="/savings/my-account/",
                    notification_type='SUCCESS'
                )

                # Notify admins and officers
                notify_staff_and_admins(
                    title="New Member Registered",
                    message=f"{profile.member_id} - {user.get_full_name()} has been enrolled by {request.user.username}.",
                    link=f"/members/{profile.id}/",
                    notification_type='INFO'
                )

            messages.success(request, f"Member '{profile.member_id} - {user.get_full_name()}' registered successfully!")
            return redirect('members:member_detail', pk=profile.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = MemberRegistrationForm()

    return render(request, 'members/member_create.html', {'form': form})

@login_required
def member_detail_view(request, pk):
    profile = get_object_or_404(MemberProfile.objects.select_related('user', 'assigned_officer'), pk=pk)

    # Permission check: Members can only view their own profile; Staff/Admins can view any
    if request.user.is_member_user and hasattr(request.user, 'member_profile') and request.user.member_profile.pk != profile.pk:
        messages.error(request, "Access restricted.")
        return redirect('core:dashboard')

    # Get savings account & transactions
    savings_account = getattr(profile, 'savings_account', None)
    savings_transactions = []
    if savings_account:
        savings_transactions = savings_account.transactions.select_related('processed_by').order_by('-created_at')[:10]

    # Get loans
    loans = profile.loans.order_by('-applied_at')

    return render(request, 'members/member_detail.html', {
        'profile': profile,
        'savings_account': savings_account,
        'savings_transactions': savings_transactions,
        'loans': loans,
    })

from django.utils import timezone

@officer_required
def member_edit_view(request, pk):
    profile = get_object_or_404(MemberProfile, pk=pk)
    user = profile.user

    if request.method == 'POST':
        form = MemberProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update user fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data.get('email', '')
            user.phone = form.cleaned_data['phone']
            if 'member_photo' in request.FILES:
                user.profile_picture = request.FILES['member_photo']
            user.save()

            form.save()
            messages.success(request, f"Profile for {profile.member_id} updated successfully.")
            return redirect('members:member_detail', pk=profile.pk)
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
        }
        form = MemberProfileEditForm(instance=profile, initial=initial_data)

    return render(request, 'members/member_edit.html', {
        'form': form,
        'profile': profile
    })

@officer_required
def member_approve_view(request, pk):
    profile = get_object_or_404(MemberProfile, pk=pk)
    
    with transaction.atomic():
        profile.status = 'ACTIVE'
        profile.reviewed_by = request.user
        profile.reviewed_at = timezone.now()
        profile.rejection_reason = None
        profile.save()

        # Activate user login
        profile.user.is_active = True
        profile.user.save(update_fields=['is_active'])

        # Notify Member
        notify_user(
            user=profile.user,
            title="Account Approved!",
            message=f"Your membership ({profile.member_id}) has been approved by officer {request.user.username}. You can now log in and manage your savings & loans.",
            link="/savings/my-account/",
            notification_type='SUCCESS'
        )

    messages.success(request, f"Member {profile.member_id} ({profile.user.get_full_name()}) has been APPROVED and activated.")
    return redirect('members:member_detail', pk=profile.pk)

@officer_required
def member_reject_view(request, pk):
    profile = get_object_or_404(MemberProfile, pk=pk)
    reason = request.POST.get('reason', 'KYC documentation or requirements could not be verified.')

    with transaction.atomic():
        profile.status = 'REJECTED'
        profile.reviewed_by = request.user
        profile.reviewed_at = timezone.now()
        profile.rejection_reason = reason
        profile.save()

        # Deactivate user login
        profile.user.is_active = False
        profile.user.save(update_fields=['is_active'])

        notify_user(
            user=profile.user,
            title="Membership Application Rejected",
            message=f"Your application was rejected. Reason: {reason}",
            link=None,
            notification_type='DANGER'
        )

    messages.warning(request, f"Member application {profile.member_id} has been marked as REJECTED.")
    return redirect('members:member_detail', pk=profile.pk)
