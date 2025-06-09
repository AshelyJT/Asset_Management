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
    path('asset_management/notifications', views.show_notifications, name='notifications'),
    path('asset_management/individual_assets', views.individual_assets_view, name='individual_assets'),
    path('asset_management/asset_detail/<str:asset_tag>/', views.asset_detail, name='asset_detail'),
    path('asset_management/inquire/', views.inquire_asset, name='inquire_asset'),
    path('asset_management/reports/', views.reports, name='reports'),
    path('asset_management/bulk_assets/', views.bulk_assets, name='bulk_assets'),
]
