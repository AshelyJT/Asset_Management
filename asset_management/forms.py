from django import forms
from .models import Asset, Department

class TransferAssetForm(forms.Form):
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.all(),
        label='Asset',
        empty_label="Select an Asset",
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'})
    )

    from_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label='From Department',
        empty_label="Select a Department",
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'})
    )

    to_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label='To Department',
        empty_label="Select a Department",
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'})
    )

    reason = forms.CharField(max_length=200, label='Reason for Transfer', widget=forms.Textarea)
