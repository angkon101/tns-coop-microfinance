from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_dispatcher, name='dashboard'),
    path('portal/member/', views.member_dashboard, name='member_dashboard'),
    path('portal/officer/', views.officer_dashboard, name='officer_dashboard'),
    path('portal/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('portal/collection-sheet/', views.collection_sheet_view, name='collection_sheet'),
    path('portal/daily-sheet/', views.collection_sheet_view, name='daily_sheet'),
    path('portal/reports/', views.financial_reports_view, name='financial_reports'),
]
