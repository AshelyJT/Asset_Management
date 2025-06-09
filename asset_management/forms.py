from django import forms
from .models import *


class TransferAssetForm(forms.Form):
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

class Modal_TransferAssetForm(forms.Form):
    to_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label="To Department: ",
        empty_label="Select a Department",
        widget=forms.Select(attrs={"class": "form-control", "required": "required"}),
    )

    reason = forms.CharField(
        max_length=200, label="Reason for Transfer: ", widget=forms.Textarea
    )


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset  # ✅ Links form to the Asset model
        fields = ['name', 'category', 'model', 'serial_number', 'status', 'location']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
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
        fields = ['asset_type', 'description', 'quantity', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            