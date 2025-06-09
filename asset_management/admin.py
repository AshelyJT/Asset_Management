from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'category', 'location', 'status', 'asset_tag')
    list_filter = ('category', 'status', 'location')
    search_fields = ('asset_tag', 'serial_number', 'name')
    date_hierarchy = 'purchase_date'

# Register all models
admin.site.register(Department)
admin.site.register(Vendor)
admin.site.register(AssetCategory)
admin.site.register(AssetTransfer)
admin.site.register(BulkAsset)

@admin.register(AssetInquiry)
class AssetInquiryAdmin(admin.ModelAdmin):
    list_display = ('user', 'asset_type', 'quantity', 'priority', 'status', 'submitted_date',)
    list_filter = ('status', 'priority', 'asset_type',)
    search_fields = ('user__username', 'description',)
    readonly_fields = ('submitted_date',)
    fieldsets = (
        (None, {
            'fields': ('user', 'asset_type', 'description', 'quantity',)
        }),
        ('Priority Information', {
            'fields': ('priority',)
        }),
        ('Status', {
            'fields': ('status', 'submitted_date',)
        }),
    )
