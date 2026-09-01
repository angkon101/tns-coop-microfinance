from django.db import models
from django.conf import settings
import uuid

class MemberProfile(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Officer Approval'),
        ('ACTIVE', 'Active / Approved'),
        ('REJECTED', 'Application Rejected'),
        ('INACTIVE', 'Inactive'),
    )
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    member_id = models.CharField(max_length=30, unique=True, blank=True)
    father_or_husband_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    nid_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="National ID (NID)")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='MALE')
    date_of_birth = models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    present_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    
    # Nominee Details
    nominee_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_relation = models.CharField(max_length=50, blank=True, null=True)
    nominee_nid = models.CharField(max_length=50, blank=True, null=True)
    nominee_phone = models.CharField(max_length=20, blank=True, null=True)

    # Document & Identification Photos
    member_photo = models.ImageField(upload_to='members/photos/', blank=True, null=True, verbose_name="Photo of Member")
    nid_photo = models.ImageField(upload_to='members/nid/', blank=True, null=True, verbose_name="Photo of NID")
    nominee_photo = models.ImageField(upload_to='members/nominees/', blank=True, null=True, verbose_name="Photo of Nominee")

    # Management & Officer Assignment
    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_members',
        limit_choices_to={'role': 'OFFICER'}
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    
    # KYC Review & Approval Tracking
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_members'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    joined_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.member_id:
            # Auto-generate Member ID like TNS-0001
            last_member = MemberProfile.objects.exclude(member_id='').order_by('-id').first()
            if last_member and last_member.id:
                next_id = last_member.id + 1
            else:
                next_id = 1
            self.member_id = f"TNS-MEM-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member_id} - {self.user.get_full_name() or self.user.username}"

    def get_status_badge(self):
        badges = {
            'ACTIVE': 'badge-success',
            'INACTIVE': 'badge-secondary',
            'PENDING': 'badge-warning',
            'REJECTED': 'badge-danger',
        }
        return badges.get(self.status, 'badge-info')
