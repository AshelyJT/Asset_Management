from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

#URL config
urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True, next_page='home'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('protected/', views.ProtectedView.as_view(), name='protected'),
    path('back_to_landing_page/', views.back_to_landing_page, name='back_to_landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_as_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='mark_all_notifications_read'),
    path('notifications/count/', views.notification_count, name='notification_count'),
    path('asset_management/', views.individual_assets_view, name='individual_assets'),
    path('asset_detail/<str:asset_tag>/', views.asset_detail, name='asset_detail'),
    path('inquire/', views.inquire_asset, name='inquire_asset'),
    path('reports/', views.reports, name='reports'),
    path('bulk_assets/', views.bulk_assets, name='bulk_assets'),
    path('reports/assets/', views.asset_reports, name='asset_reports'),
    path('incoming/', views.incoming_equipment_list, name='incoming_equipment_list'),
    path('incoming/<int:pk>/', views.incoming_equipment_detail, name='incoming_equipment_detail'),
    path('outgoing-equipment/', views.outgoing_equipment_list, name='outgoing_equipment_list'),
    path('my-requests/', views.my_equipment_requests, name='my_equipment_requests'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
]
