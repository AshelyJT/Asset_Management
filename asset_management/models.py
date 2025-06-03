from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    branch = models.ForeignKey(
        "Department", on_delete=models.SET_NULL, null=True, blank=True)


class Department(models.Model):
    name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=50, null=True, blank=True)
    branch_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.branch_code})"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    branch = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.branch}"


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


class Asset(models.Model):
    ASSET_STATUS = [
        ("OPERATIONAL", "Operational"),
        ("NON_OPERATIONAL", "Non-Operational"),
        ("DECOMMISSIONED", "Decommissioned"),
        ("LOST", "Lost"),
        ("STOLEN", "Stolen"),
    ]

    asset_tag = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20, choices=ASSET_STATUS, default="OPERATIONAL"
    )
    location = models.ForeignKey(Department, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.model} ({self.asset_tag})"


class AssetTransfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    from_department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="transfers_out",
    )
    to_department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="transfers_in"
    )
    transfer_date = models.DateField(auto_now_add=True)
    reason = models.TextField()
    transfer_status = models.CharField(max_length=20, default="PENDING")
    admin_status = models.CharField(max_length=20, default="unseen")
    user_status = models.CharField(max_length=20, default="unseen")

    def __str__(self):
        return f"Transfer of {self.asset.name} to {self.to_department}"


class BulkAsset(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    purchase_date = models.DateField()
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=[
        ('AVAILABLE', 'Available'),
        ('IN USE', 'In Use'),
        ('DEPLETED', 'Depleted')
    ], default='AVAILABLE')
    location = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} - Qty: {self.quantity}"
