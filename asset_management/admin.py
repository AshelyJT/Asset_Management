from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.
from django.contrib import admin
from .models import *

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_tag', 'name', 'category', 'status')
    list_filter = ('category', 'status', 'location')
    search_fields = ('asset_tag', 'serial_number', 'name')
    date_hierarchy = 'purchase_date'

# Register all other models similarly
admin.site.register(Department)
admin.site.register(Vendor)
admin.site.register(AssetCategory)
admin.site.register(AssetTransfer)
admin.site.register(UserProfile)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'branch', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'branch')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
admin.site.register(CustomUser, CustomUserAdmin)