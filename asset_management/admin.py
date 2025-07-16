from django.contrib import admin
from .models import *

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'category', 'status', 'asset_tag', 'transfer_status')
    list_filter = ('category', 'status')
    search_fields = ('asset_tag', 'serial_number', 'name')
    date_hierarchy = 'purchase_date'

# Register all models
admin.site.register(Profile)
admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Vendor)
admin.site.register(AssetCategory)
admin.site.register(IncomingEquipment)


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = ('asset', 'from_department', 'to_department', 'transfer_date', 'transfer_status', 'sent_by', 'received_by')
    list_filter = ('transfer_status', 'from_department', 'to_department', 'transfer_date')
    search_fields = ('asset__name', 'from_department__name', 'to_department__name', 'reason')
    readonly_fields = ('transfer_date',)
    fieldsets = (
        (None, {
            'fields': ('asset',)
        }),
        ('Transfer Origin', {
            'fields': ('from_department', 'from_branch',)
        }),
        ('Transfer Destination', {
            'fields': ('to_department', 'to_branch',)
        }),
        ('Transfer Details', {
            'fields': ('transfer_date', 'reason',)
        }),
        ('Status Information', {
            'fields': ('transfer_status', 'sent_by', 'received_by')
        }),
    )

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
    
@admin.register(BulkAsset)
class BulkAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'total_quantity', 'available_quantity','in_use_quantity', 'depleted_quantity', 'location')
    list_filter = ('category', 'location')
    search_fields = ('name', 'category__name')
    readonly_fields = ('total_quantity',)
