from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.views import View
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.core.paginator import Paginator
from xhtml2pdf import pisa
import openpyxl
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from .models import *
from .forms import *


# Create your views here.
def landing_page(request):
    return render(request, "landing_page.html")


def login_view(request):
    error_message = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = (
                request.POST.get("next") or request.GET.get("next") or "dashboard"
            )
            return redirect(next_url)
        else:
            error_message = "Invalid username or password. Please try again."
    return render(request, "login.html", {"error": error_message})


def back_to_landing_page(request):
    if request.method == "POST":
        logout(request)
        return redirect("landing_page")
    return render(request, "landing_page.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    total_assets = Asset.objects.count()
    context = {
        "total_assets": total_assets,
        "total_bulk_assets": BulkAsset.objects.aggregate(
            total_quantity=Sum("quantity")
        )["total_quantity"]
        or 0,
    }
    return render(request, "dashboard.html", context)


class ProtectedView(LoginRequiredMixin, View):
    login_url = "/login"
    redirect_field_name = "redirect_to"

    def get(self, request):
        return render(request, "protected.html")


@login_required
def individual_assets_view(request):
    assets = Asset.objects.all()
    context = {
        "assets": assets,
        "asset_categories": AssetCategory.objects.all(),
    }
    return render(request, "individual_assets.html", context)


@login_required
def asset_detail(request, asset_tag):
    form = Modal_TransferAssetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        selected_asset = get_object_or_404(Asset, asset_tag=asset_tag)
        to_department = form.cleaned_data["to_department"]
        reason = form.cleaned_data["reason"]
        asset_transfer = AssetTransfer.objects.create(
            asset=selected_asset,
            from_department=selected_asset.location,
            to_department=to_department,
            reason=reason,
        )
        asset_transfer.save()
        create_notification(
            recipient=request.user,
            sender=request.user,
            notification_type="ASSET_CHECKOUT",
            title=f"{selected_asset.location} - Asset Transfer for {selected_asset.name} {selected_asset.category} ({selected_asset.asset_tag})",
            message=f"This asset {selected_asset.name} {selected_asset.model} with Serial number {selected_asset.serial_number} has been sent to {to_department.name} - {to_department.branch_name} for this reason: {reason}",
            related_object=asset_transfer,
        )
        messages.success(request, "Asset transfer request submitted successfully.")
        return redirect("asset_detail", asset_tag=asset_tag)
    selected_asset = get_object_or_404(Asset, asset_tag=asset_tag)
    context = {
        "selected_asset": selected_asset,
        "form": form,
    }
    return render(request, "asset_detail.html", context)


@login_required
def reports(request):
    assets = Asset.objects.all()
    context = {
        "assets": assets,
    }
    return render(request, "reports.html", context)


@login_required
def bulk_assets(request):
    context = {
        "form": BulkAssetForm(),
        "bulk_assets": BulkAsset.objects.all(),
        "total_bulk_assets": BulkAsset.objects.aggregate(
            total_quantity=Sum("quantity")
        )["total_quantity"]
        or 0,
    }
    return render(request, "bulk_assets.html", context)


@login_required
def inquire_asset(request):
    if request.method == "POST":
        form = AssetInquiryForm(request.POST, user=request.user)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user
            inquiry.save()
            messages.success(
                request, "Your asset inquiry has been submitted successfully!"
            )
            return redirect("inquire_asset")
    else:
        form = AssetInquiryForm(user=request.user)

    return render(request, "inquire_asset.html", {"form": form})


@login_required
def asset_reports(request):
    assets = Asset.objects.select_related("category", "vendor", "location").all()
    form = AssetReportFilterForm(request.GET or None)

    if form.is_valid():
        status = form.cleaned_data.get("status")
        category = form.cleaned_data.get("category")
        location = form.cleaned_data.get("location")
        vendor = form.cleaned_data.get("vendor")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")
        export_format = form.cleaned_data.get("export_format")

        if status:
            assets = assets.filter(status=status)
        if category:
            assets = assets.filter(category=category)
        if location:
            assets = assets.filter(location=location)
        if vendor:
            assets = assets.filter(vendor=vendor)
        if date_from:
            assets = assets.filter(purchase_date__gte=date_from)
        if date_to:
            assets = assets.filter(purchase_date__lte=date_to)

        if export_format:
            if export_format == "excel":
                return export_to_excel(assets)
            elif export_format == "pdf":
                return export_to_pdf(assets)

    context = {
        "assets": assets,
        "form": form,
        "total_assets": assets.count(),
    }
    return render(request, "reports/asset_reports.html", context)


def export_to_excel(queryset):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=assets_report.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Assets Report"

    # Column headers
    headers = [
        "Asset Tag",
        "Name",
        "Category",
        "Model",
        "Serial Number",
        "Purchase Date",
        "Vendor",
        "Status",
        "Location",
        "Notes",
    ]
    ws.append(headers)

    # Data rows
    for asset in queryset:
        ws.append(
            [
                asset.asset_tag,
                asset.name,
                str(asset.category),
                asset.model,
                asset.serial_number,
                asset.purchase_date.strftime("%Y-%m-%d"),
                str(asset.vendor),
                asset.get_status_display(),
                str(asset.location),
                asset.notes,
            ]
        )

    # Auto-size columns
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column_letter].width = adjusted_width

    wb.save(response)
    return response


def export_to_pdf(queryset):
    template_path = "reports/pdf_template.html"
    context = {"assets": queryset, "today": datetime.now()}

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="assets_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("We had some errors generating the PDF")
    return response


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    form = NotificationFilterForm(request.GET or None)

    if form.is_valid():
        notification_type = form.cleaned_data.get("notification_type")
        is_read = form.cleaned_data.get("is_read")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")

        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        if is_read == "read":
            notifications = notifications.filter(is_read=True)
        elif is_read == "unread":
            notifications = notifications.filter(is_read=False)
        if date_from:
            notifications = notifications.filter(created_at__gte=date_from)
        if date_to:
            notifications = notifications.filter(created_at__lte=date_to)

    # Pagination
    paginator = Paginator(notifications, 20)  # Show 20 notifications per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "form": form,
        "unread_count": Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count(),
    }
    return render(request, "notifications/list.html", context)

def create_notification(
    sender, recipient, notification_type, title, message, related_object=None
):
    notification = Notification(
        sender=sender,
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        related_object_id=related_object.id if related_object else None,
        related_content_type=ContentType.objects.get_for_model(related_object)
        if related_object
        else None,
    )
    notification.save()
    return notification

@login_required
def mark_notification_as_read(request, pk):
    notification = Notification.objects.get(pk=pk, recipient=request.user)
    notification.mark_as_read()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})
    return redirect("notifications_list")


@login_required
def mark_all_as_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})
    return redirect("notifications_list")


@login_required
def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return JsonResponse({"count": count})
    return JsonResponse({"count": 0})
