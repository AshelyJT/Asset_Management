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


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    fieldsets = (
        (None, {
            'fields': ('recipient', 'sender', 'notification_type')
        }),
        ('Content', {
            'fields': ('title', 'message', 'related_object_id', 'related_content_type')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'created_at')
        }),
    )