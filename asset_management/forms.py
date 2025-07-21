from django.core.exceptions import ValidationError
from django import forms
from .models import *
from django.utils import timezone


class Modal_TransferAssetForm(forms.Form):
    empty_label = "--------------"
    
    to_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label="To Department:",
        empty_label=empty_label,
        widget=forms.Select(attrs={
            "class": "form-control",
            "required": "required"
        }),
    )
    
    to_branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        label="To Branch:",
        empty_label=empty_label,
        widget=forms.Select(attrs={
            "class": "form-control",
            "required": "required"
        }),
    )

    reason = forms.CharField(
        max_length=200,
        label="Reason for Transfer:",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3
        })
    )
    
class Modal_BulkTransferAssetForm(forms.Form):
    empty_label = "--------------"
    
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity:",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "required": "required"
        })
    )
    to_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label="To Department:",
        empty_label=empty_label,
        widget=forms.Select(attrs={
            "class": "form-control",
            "required": "required"
        }),
    )
    
    to_branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        label="To Branch:",
        empty_label=empty_label,
        widget=forms.Select(attrs={
            "class": "form-control",
            "required": "required"
        }),
    )

    reason = forms.CharField(
        max_length=200,
        label="Reason for Transfer:",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3
        })
    )


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ["name", "category", "model", "serial_number", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "serial_number": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class BulkAssetForm(forms.ModelForm):
    class Meta:
        model = BulkAsset
        fields = [
            "name", "category", "purchase_date", 
            "vendor", "status"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),        
            "purchase_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "vendor": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class AssetInquiryForm(forms.ModelForm):
    class Meta:
        model = AssetInquiry
        fields = ["asset_type", "description", "quantity", "priority"]
        widgets = {
            "asset_type": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class AssetReportFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + Asset.ASSET_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    category = forms.ModelChoiceField(
        queryset=AssetCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    assigned_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        }),
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        }),
    )

    export_format = forms.ChoiceField(
        choices=[("", "Select export format"), ("excel", "Excel"), ("pdf", "PDF")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class NotificationFilterForm(forms.Form):
    notification_type = forms.ChoiceField(
        choices=[("", "All Types")] + Notification.NOTIFICATION_TYPES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_read = forms.ChoiceField(
        choices=[("", "All"), ("read", "Read"), ("unread", "Unread")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        }),
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        }),
    )


class ReceiveEquipmentForm(forms.ModelForm):
    class Meta:
        model = AssetTransfer  # Changed from IncomingEquipment to AssetTransfer
        fields = ['received_date', 'notes']
        widgets = {
            'received_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date()
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any notes about the condition or contents'
            }),
        }

    def clean_received_date(self):
        received_date = self.cleaned_data.get('received_date')
        if received_date and received_date > timezone.now().date():
            raise ValidationError("Received date cannot be in the future")
        return received_date
    
    
class AdminRequestActionForm(forms.ModelForm):
    class Meta:
        model = AssetInquiry
        fields = ['status', 'admin_notes']
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit status choices for admins
        self.fields['status'].choices = [
            ('APPROVED', 'Approved'),
            ('DENIED', 'Denied'),
            ('FULFILLED', 'Fulfilled'),
        ]