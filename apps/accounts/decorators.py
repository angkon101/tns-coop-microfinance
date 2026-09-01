from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_admin_user or request.user.is_superuser):
            messages.error(request, "Access restricted to Administrators only.")
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def officer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_officer_user or request.user.is_admin_user or request.user.is_superuser):
            messages.error(request, "Access restricted to Officers and Administrators.")
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def member_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_member_user:
            messages.error(request, "Access restricted to Members.")
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
