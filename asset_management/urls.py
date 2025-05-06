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
    path('transfer_asset/', views.transfer_asset, name='transfer_asset'),
    path('notifications/', views.show_notifications, name='notifications'),
    path('asset_management/', views.asset_management, name='asset_management'),
    path('reports/', views.reports, name='reports'),
]
