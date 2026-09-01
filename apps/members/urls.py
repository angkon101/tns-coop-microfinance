from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.member_list_view, name='member_list'),
    path('create/', views.member_create_view, name='member_create'),
    path('<int:pk>/', views.member_detail_view, name='member_detail'),
    path('<int:pk>/edit/', views.member_edit_view, name='member_edit'),
    path('<int:pk>/approve/', views.member_approve_view, name='member_approve'),
    path('<int:pk>/reject/', views.member_reject_view, name='member_reject'),
]
