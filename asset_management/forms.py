from django.core.exceptions import ValidationError
from django import forms
from .models import *
from django.utils import timezone


""" class TransferAssetForm(forms.Form):
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.all(),
        label="Asset",
        empty_label="Select an Asset",
        widget=forms.Select(attrs={"class": "form-control", "required": "required"}),
    )

    to_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label="To Department",
        empty_label="Select a Department",
        widget=forms.Select(attrs={"class": "form-control", "required": "required"}),
    )

    reason = forms.CharField(
        max_length=200, label="Reason for Transfer", widget=forms.Textarea
    )
 """

class Modal_TransferAssetForm(forms.Form):
    empty_label="--------------"
    to_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label="To Department: ",
        empty_label=empty_label,
        widget=forms.Select(attrs={"class": "form-control", "required": "required"}),
    )
    
    to_branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        label="To Branch: ",
        empty_label=empty_label,
        widget=forms.Select(attrs={"class": "form-control", "required": "required"}),
    )

    reason = forms.CharField(
        max_length=200, label="Reason for Transfer: ", widget=forms.Textarea
    )


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset  # ✅ Links form to the Asset model
        fields = ["name", "category", "model", "serial_number", "status",]

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
            "name",
            "category",
            "quantity",
            "purchase_date",
            "vendor",
            "status",
            "location",
        ]


class AssetInquiryForm(forms.ModelForm):
    class Meta:
        model = AssetInquiry
        fields = ["asset_type", "description", "quantity", "priority"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class AssetReportFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + Asset.ASSET_STATUS,
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
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
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
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    
    
class ReceiveEquipmentForm(forms.ModelForm):
    class Meta:
        model = IncomingEquipment
        fields = ['received_date', 'notes']
        widgets = {
            'received_date': forms.DateInput(attrs={'type': 'date', 'max': timezone.now().date()}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter any notes about the condition or contents'}),
        }

    def clean_received_date(self):
        received_date = self.cleaned_data.get('received_date')
        if received_date and received_date > timezone.now().date():
            raise ValidationError("Received date cannot be in the future")
        return received_date