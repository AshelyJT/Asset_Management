from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Asset, AssetTransfer
from .forms import TransferAssetForm


# Create your views here.
def landing_page(request):
    return render(request, 'landing_page.html')


def login_view(request):    
    error_message = ''
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            error_message = "Invalid username or password. Please try again."
    return render(request, 'login.html', {'error':error_message})


def back_to_landing_page(request):
    if request.method == "POST":
        logout(request)
        return redirect('landing_page')
    return render(request, 'landing_page.html')


def logout_view(request):
    logout(request)
    return redirect('login')
        

@login_required
def dashboard(request):
    # Get real data from your models
    total_assets = Asset.objects.count()
    
    context = {
        'total_assets': total_assets,
    }  
    
    return render(request, 'dashboard.html', context)


class ProtectedView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        return render(request, 'protected.html')
    

@login_required
def transfer_asset(request):
    if request.method == 'POST':
        form = TransferAssetForm(request.POST)
        if form.is_valid():
            asset = form.cleaned_data['asset']
            to_department = form.cleaned_data['to_department']
            reason = form.cleaned_data['reason']
            from_department = form.cleaned_data['from_department']

            asset_transfer = AssetTransfer.objects.create(
                asset=asset,
                from_department=from_department,
                to_department=to_department,
                reason=reason
            )
            asset_transfer.save()
            messages.success(request, "Asset transfer request submitted successfully.")
            return redirect('transfer_asset')
        else:
            messages.error(request, "Error in form submission. Please check the details.")
    
    else:
        form = TransferAssetForm()

    return render(request, 'asset_transfer.html', {'form': form})


@login_required
def show_notifications(request):
    # Fetch notifications from the database or any other source
    notifications = [
        {'message': 'Asset transfer request approved.', 'timestamp': '2023-10-01 10:00'},
        {'message': 'New asset added to inventory.', 'timestamp': '2023-10-02 12:00'},
        {'message': 'Asset maintenance scheduled.', 'timestamp': '2023-10-03 14:00'},
    ]

    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def asset_management(request):
    asset_transfers = AssetTransfer.objects.all()
    assets = Asset.objects.all()
    context = {
        'asset_transfers': asset_transfers,
        'assets': assets,
    }
    return render(request, 'asset_management.html', context)

@login_required
def reports(request):
    assets = Asset.objects.all()
    context = {
        'assets': assets,
    }
    return render(request, 'reports.html', context)