from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('registration-submitted/', views.registration_submitted_view, name='registration_submitted'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('officers/', views.officer_list_view, name='officer_list'),
    path('officers/<int:user_id>/toggle-status/', views.officer_toggle_status, name='officer_toggle_status'),
]
