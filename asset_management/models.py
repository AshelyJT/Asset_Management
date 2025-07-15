from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_department = models.ForeignKey(
        "Department", on_delete=models.SET_NULL, null=True, blank=True
    )
    user_branch = models.ForeignKey(
        "Branch", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.user_branch}"


class Branch(models.Model):
    branch_name = models.CharField(max_length=100, unique=True)
    branch_code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        if self.branch_name=="OK HeadOffice":
            return f"{self.branch_name}"
        else:
            return f"BR{self.branch_code} - {self.branch_name}"

    class Meta:
        verbose_name_plural = "Branches"


class Department(models.Model):
    department_name = models.CharField(max_length=100, unique=True)
    department_code = models.CharField(max_length=10, blank=True, null=True)
    def __str__(self):
        if self.department_code:
            return f"{self.department_name} ({self.department_code})"
        else:
            return f"{self.department_name}"


class Vendor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name


class AssetCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Asset Categories"


class Asset(models.Model):
    ASSET_STATUS_CHOICES = [
        ("OPERATIONAL", "Operational"),
        ("NON_OPERATIONAL", "Non-Operational"),
        ("DECOMMISSIONED", "Decommissioned"),
        ("LOST", "Lost"),
        ("STOLEN", "Stolen"),
    ]
    
    TRANSFER_STATUS = [
        ("PROCESSING", "PROCESSING"),
        ("RECEIVED", "RECEIVED"),
    ]

    asset_tag = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20, choices=ASSET_STATUS_CHOICES, default="OPERATIONAL"
    )
    assigned_department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="assets", null=True, blank=True
    )
    assigned_branch = models.ForeignKey(
        Branch, on_delete=models.PROTECT, related_name="assets", null=True, blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transfer_status = models.CharField(choices=TRANSFER_STATUS, default="RECEIVED")

    def __str__(self):
        return f"{self.name} {self.model} ({self.asset_tag})"


class AssetTransfer(models.Model):
    transfer_options = [
        ("PENDING", "PENDING"),
        ("RECEIVED", "RECEIVED"),
    ]
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    from_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="transfers_out",
        default=None,
        null=True,
        blank=True,
    )
    from_branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="transfers_out",
        null=True,
        blank=True,
    )
    to_department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="transfers_in"
    )
    to_branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="transfers_in",
        null=True,
        blank=True,
    )
    transfer_date = models.DateField(auto_now_add=True)
    reason = models.TextField()
    transfer_status = models.CharField(choices=transfer_options, default="PENDING")
    sent_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transfers_sent",
        null=True,
        blank=True,
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transfers_received",
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)
    received_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Transfer of {self.asset.name} to {self.to_department}"


class BulkAsset(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    purchase_date = models.DateField()
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=[
            ("AVAILABLE", "Available"),
            ("IN USE", "In Use"),
            ("DEPLETED", "Depleted"),
        ],
        default="AVAILABLE",
    )
    location = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} - Qty: {self.quantity}"


class AssetInquiry(models.Model):
    ASSET_TYPES = [
        ("LAPTOP", "Laptop"),
        ("DESKTOP", "Desktop Computer"),
        ("PRINTER", "Printer"),
        ("PHONE", "Phone"),
        ("TABLET", "Tablet"),
        ("OTHER", "Other Equipment"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    description = models.TextField(help_text="Why is this equipment needed?")
    quantity = models.PositiveIntegerField(default=1)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM"
    )
    submitted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        default="PENDING",
        choices=[
            ("PENDING", "Pending Review"),
            ("APPROVED", "Approved"),
            ("DENIED", "Denied"),
            ("FULFILLED", "Fulfilled"),
        ],
    )
    
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='processed_inquiries'
    )
    processed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_asset_type_display()} request by {self.user.username}"

    class Meta:
        verbose_name_plural = "Asset Inquiries"
        ordering = ["-submitted_date"]


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("ASSET_INQUIRY", "Asset Inquiry"),
        ("ASSET_UPDATED", "Asset Updated"),
        ("ASSET_DELETED", "Asset Deleted"),
        ("MAINTENANCE_DUE", "Maintenance Due"),
        ("MAINTENANCE_COMPLETED", "Maintenance Completed"),
        ("ASSET_CHECKOUT", "Asset Checked Out"),
        ("ASSET_CHECKIN", "Asset Checked In"),
        ("SYSTEM_ALERT", "System Alert"),
    ]

    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_content_type = models.ForeignKey(
        "contenttypes.ContentType", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    @property
    def is_recent(self):
        return (timezone.now() - self.created_at).days < 1


class IncomingEquipment(models.Model):
    RECEIVING_STATUS = [
        ("PENDING", "Pending"),
        ("RECEIVED", "Received"),
        ("RETURNED", "Returned to Sender"),
    ]

    asset = models.ForeignKey("Asset", on_delete=models.SET_NULL, null=True, blank=True)
    to_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="incoming_equipment",
        null=True,
        blank=True,
    )
    from_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="outgoing_equipment",
        null=True,
        blank=True,
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="received_equipment",
        null=True,
        blank=True,
    )
    received_date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=20, choices=RECEIVING_STATUS, default="PENDING"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-received_date"]
        verbose_name = "Incoming Equipment"
        verbose_name_plural = "Incoming Equipment"

    def __str__(self):
        return f"Incoming #{self.id}"

    def mark_as_received(self):
        self.status = "RECEIVED"
        self.save()
