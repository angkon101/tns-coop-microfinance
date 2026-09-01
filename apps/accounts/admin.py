from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_approved', 'is_staff', 'is_active')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Microfinance Info', {'fields': ('role', 'phone', 'address', 'profile_picture', 'is_approved')}),
    )
