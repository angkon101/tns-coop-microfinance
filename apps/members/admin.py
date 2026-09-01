from django.contrib import admin
from .models import MemberProfile

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'user', 'nid_number', 'status', 'assigned_officer', 'joined_date')
    list_filter = ('status', 'gender', 'joined_date')
    search_fields = ('member_id', 'user__first_name', 'user__last_name', 'user__phone', 'nid_number')
