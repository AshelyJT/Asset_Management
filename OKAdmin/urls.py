"""
URL configuration for OKAdmin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from asset_management import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing_page'),
    path('asset_management/', include('asset_management.urls')),
    path('asset_management/login', views.login_view, name='login'),
    path('asset_management/logout', views.logout_view, name='logout'),
    path('asset_management/protected', views.ProtectedView.as_view(), name='protected'),
    path('asset_management/back_to_landing_page', views.back_to_landing_page, name='back_to_landing_page'),
    path('asset_management/dashboard', views.dashboard, name='dashboard'),
    path('asset_management/individual_assets', views.individual_assets_view, name='individual_assets'),
    path('asset_management/asset_detail/<str:asset_tag>/', views.asset_detail, name='asset_detail'),
    path('asset_management/inquire/', views.inquire_asset, name='inquire_asset'),
    path('asset_management/reports/', views.reports, name='reports'),
    path('asset_management/bulk_assets/', views.bulk_assets, name='bulk_assets'),
    path('asset_management/reports/assets/', views.asset_reports, name='asset_reports'),
    path('asset_management/notifications/', views.notifications_list, name='notifications_list'),
    path('asset_management/notifications/<int:pk>/mark-read/', views.mark_notification_as_read, name='mark_notification_read'),
    path('asset_management/notifications/mark-all-read/', views.mark_all_as_read, name='mark_all_notifications_read'),
    path('asset_management/notifications/count/', views.notification_count, name='notification_count'),
    path('incoming/', views.incoming_equipment_list, name='incoming_equipment_list'),
    path('incoming/<int:pk>/', views.incoming_equipment_detail, name='incoming_equipment_detail'),
]
