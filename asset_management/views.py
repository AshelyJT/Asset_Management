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
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


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
    user = request.user
    user_branch = user.profile.user_branch.branch_name
    total_assets = Asset.objects.filter(
        assigned_branch__branch_name=user_branch
    ).count()
    incoming_equipment_count = AssetTransfer.objects.filter(
        to_branch=request.user.profile.user_branch, transfer_status="PENDING"
    ).count()
    outgoing_equipment_count = AssetTransfer.objects.filter(
        from_branch=request.user.profile.user_branch, transfer_status="PENDING"
    ).count()
    inquiries_count = AssetInquiry.objects.filter(
        user=request.user, status="PENDING"
    ).count()
    context = {
        "total_assets": total_assets,
        "total_bulk_assets": BulkAsset.objects.aggregate(
            total_quantity=Sum("quantity")
        )["total_quantity"]
        or 0,
        "incoming_equipment_count": incoming_equipment_count,
        "outgoing_equipment_count": outgoing_equipment_count,
        "inquiries_count": inquiries_count,
    }
    return render(request, "dashboard.html", context)


class ProtectedView(LoginRequiredMixin, View):
    login_url = "/login"
    redirect_field_name = "redirect_to"

    def get(self, request):
        return render(request, "protected.html")


@login_required
def individual_assets_view(request):
    user = request.user
    if not hasattr(user, "profile") or not user.profile.user_branch:
        messages.error(request, "Your profile is not set up correctly.")
        return redirect("dashboard")
    user_branch = user.profile.user_branch
    assets = Asset.objects.filter(assigned_branch=user_branch)
    context = {
        "assets": assets,
        "asset_categories": AssetCategory.objects.all(),
    }
    return render(request, "assets/individual_assets.html", context)


@login_required
def asset_detail(request, asset_tag):
    selected_asset = get_object_or_404(Asset, asset_tag=asset_tag)
    if selected_asset.transfer_status == "PROCESSING":
        return render(request, "assets/asset_detail.html", {"show_error_modal": True, "selected_asset":selected_asset})
    else:
        form = Modal_TransferAssetForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            to_department = form.cleaned_data["to_department"]
            to_branch = form.cleaned_data["to_branch"]
            reason = form.cleaned_data["reason"]
            asset_transfer = AssetTransfer.objects.create(
                asset=selected_asset,
                from_department=Department.objects.get(
                    department_name=selected_asset.assigned_department.department_name
                ),
                from_branch=Branch.objects.get(
                    branch_name=selected_asset.assigned_branch.branch_name
                ),
                to_department=to_department,
                to_branch=to_branch,
                reason=reason,
                sent_by=request.user,
            )
            asset_transfer.save()
            selected_asset.transfer_status="PROCESSING"
            selected_asset.save()

            create_incoming_equipment(
                asset=selected_asset,
                from_department=selected_asset.assigned_department,
                notes=f"Asset transfer from {selected_asset.assigned_department} {selected_asset.assigned_branch} to {to_department.department_name} for reason: {reason}",
                status="PENDING",
            )

            create_notification(
                recipient=request.user,
                sender=request.user,
                notification_type="ASSET_CHECKOUT",
                title=f"{selected_asset.assigned_branch} - Asset Transfer for {selected_asset.name} {selected_asset.category} ({selected_asset.asset_tag})",
                message=f"This asset {selected_asset.name} {selected_asset.model} with Serial number {selected_asset.serial_number} has been sent to {to_department.department_name} - {to_branch.branch_name} for this reason: {reason}",
                related_object=asset_transfer,
            )
            messages.success(request, "Asset transfer request submitted successfully.")
            return redirect("asset_detail", asset_tag=asset_tag)
        selected_asset = get_object_or_404(Asset, asset_tag=asset_tag)
        context = {
            "selected_asset": selected_asset,
            "form": form,
        }
        return render(request, "assets/asset_detail.html", context)


def update_asset_location(asset, new_department, new_branch):
    asset.assigned_department = new_department
    asset.assigned_branch = new_branch
    asset.save()


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
    return render(request, "assets/bulk_assets.html", context)


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
            create_notification(
                recipient=request.user,
                sender=request.user,
                notification_type="ASSET_INQUIRY",
                title="Asset Inquiry Submitted",
                message=f"Requesting for {inquiry.asset_type} for this reason: {inquiry.description}",
            )
            return redirect("assets/inquire_asset")
    else:
        form = AssetInquiryForm(user=request.user)

    return render(request, "assets/inquire_asset.html", {"form": form})


@login_required
def asset_reports(request):
    assets = Asset.objects.select_related(
        "category",
        "assigned_department",
        "assigned_branch",
    ).all()
    form = AssetReportFilterForm(request.GET or None)

    if form.is_valid():
        status = form.cleaned_data.get("status")
        category = form.cleaned_data.get("category")
        assigned_branch = form.cleaned_data.get("assigned_branch")
        vendor = form.cleaned_data.get("vendor")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")
        export_format = form.cleaned_data.get("export_format")

        if status:
            assets = assets.filter(status=status)
        if category:
            assets = assets.filter(category=category)
        if assigned_branch:
            assets = assets.filter(assigned_branch=assigned_branch)
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
                str(asset.assigned_branch),
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
        related_content_type=(
            ContentType.objects.get_for_model(related_object)
            if related_object
            else None
        ),
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


@login_required
def incoming_equipment_list(request):
    user = request.user
    user_branch = user.profile.user_branch
    equipment_list = AssetTransfer.objects.filter(
        to_branch=user_branch, transfer_status="PENDING"
    ).select_related("asset", "from_department", "to_department")
    form = ReceiveEquipmentForm(request.GET or None)

    if form.is_valid():
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")

        if date_from:
            equipment_list = equipment_list.filter(expected_date__gte=date_from)
        if date_to:
            equipment_list = equipment_list.filter(expected_date__lte=date_to)

    # Order by expected date (soonest first)
    equipment_list = equipment_list.order_by("-id")

    context = {
        "equipment_list": equipment_list,
        "form": form,
    }
    return render(request, "equipment/incoming_list.html", context)


@login_required
def incoming_equipment_detail(request, pk):
    try:
        user = request.user
        
        # First verify user profile is properly configured
        try:
            profile = user.profile
            user_department = profile.user_department
            user_branch = profile.user_branch
            if not all([user_department, user_branch]):
                messages.error(request, "Your profile is missing department or branch information")
                return redirect("incoming_equipment_list")
        except AttributeError as e:
            logger.error(f"User profile error: {str(e)}")
            messages.error(request, "Your user profile is not properly configured")
            return redirect("incoming_equipment_list")

        # Get the transfer record with related asset
        try:
            equipment = get_object_or_404(
                AssetTransfer.objects.select_related('asset'),
                pk=pk,
                to_branch=user_branch,
                transfer_status="PENDING"  # Changed from PROCESSING to PENDING
            )
            asset = equipment.asset
        except Exception as e:
            logger.error(f"Equipment lookup error: {str(e)}")
            messages.error(request, "Equipment record not found or already processed")
            return redirect("incoming_equipment_list")

        if request.method == "POST" and "receive_equipment" in request.POST:
            form = ReceiveEquipmentForm(request.POST, instance=equipment)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # Update transfer record
                        equipment = form.save(commit=False)
                        equipment.received_by = user
                        equipment.transfer_status = "RECEIVED"
                        equipment.save()
                        
                        # Update asset
                        asset.transfer_status = "RECEIVED"
                        asset.save()
                        
                        # Update location
                        try:
                            update_asset_location(
                                asset=asset,
                                new_department=user_department,
                                new_branch=user_branch,
                            )
                        except Exception as loc_error:
                            logger.error(f"Location update failed: {str(loc_error)}")
                            raise ValueError("Failed to update asset location") from loc_error
                    
                    messages.success(request, "Equipment successfully received.")
                    return redirect("incoming_equipment_list")
                except Exception as e:
                    logger.error(f"Transaction failed: {str(e)}")
                    messages.error(request, f"Failed to complete receipt: {str(e)}")
                    return redirect("incoming_equipment_detail", pk=pk)
            else:
                messages.error(request, "Form contains invalid data")
                logger.warning(f"Form errors: {form.errors}")
        else:
            form = ReceiveEquipmentForm(instance=equipment)

        context = {
            "equipment": equipment,
            "form": form,
        }
        return render(request, "equipment/incoming_detail.html", context)

    except Exception as e:
        logger.exception("Unexpected error in incoming_equipment_detail")
        messages.error(request, "An unexpected error occurred while processing the request")
        return redirect("incoming_equipment_list")

def create_incoming_equipment(
    asset=None, from_department=None, to_department=None, notes="", status="PENDING"
):
    incoming_equipment = IncomingEquipment(
        asset=asset,
        from_department=from_department,
        to_department=to_department,
        notes=notes,
        status=status,
    )
    incoming_equipment.save()
    return incoming_equipment


@login_required
def outgoing_equipment_list(request):
    user = request.user
    try:
        user_branch = user.profile.user_branch
    except AttributeError:
        messages.error(request, "Your profile is not properly configured with a branch.")
        return redirect("dashboard")

    # Get all pending transfers initiated by this user from their branch
    outgoing_transfers = AssetTransfer.objects.filter(
        from_branch=user_branch,
        transfer_status="PENDING",
        sent_by=user 
    ).select_related(
        'asset',
        'to_department',
        'to_branch',
        'from_department'
    ).order_by('-transfer_date')

    # Add pagination
    paginator = Paginator(outgoing_transfers, 20)  # Show 20 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Outgoing Equipment Transfers',
    }
    return render(request, 'equipment/outgoing_list.html', context)


@login_required
def my_equipment_requests(request):
    user = request.user
    
    # Get all requests sent by this user
    requests = AssetInquiry.objects.filter(
        user=user
    ).select_related(
        'user'
    ).order_by('-submitted_date')
    
    # Add filtering
    status_filter = request.GET.get('status', None)
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(requests, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': AssetInquiry._meta.get_field('status').choices,
        'current_status': status_filter,
    }
    return render(request, 'requests/my_requests.html', context)

@login_required
def request_detail(request, pk):
    inquiry = get_object_or_404(AssetInquiry, pk=pk, user=request.user)
    
    context = {
        'inquiry': inquiry,
    }
    return render(request, 'requests/request_detail.html', context)

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def manage_requests(request):
    # Get all pending requests (or filter as needed)
    inquiries = AssetInquiry.objects.filter(
        status__in=['PENDING', 'APPROVED']
    ).select_related(
        'user'
    ).order_by('-submitted_date')
    
    # Filtering
    status_filter = request.GET.get('status', None)
    if status_filter:
        inquiries = inquiries.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(inquiries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': AssetInquiry._meta.get_field('status').choices,
        'current_status': status_filter,
    }
    return render(request, 'requests/admin/manage_requests.html', context)

@staff_member_required
def process_request(request, pk):
    inquiry = get_object_or_404(AssetInquiry, pk=pk)
    
    if request.method == 'POST':
        form = AdminRequestActionForm(request.POST, instance=inquiry)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.processed_by = request.user
            inquiry.processed_date = timezone.now()
            inquiry.save()
            
            # Create notification for the user
            create_notification(
                sender=request.user,
                recipient=inquiry.user,
                notification_type="REQUEST_UPDATE",
                title=f"Your request for {inquiry.get_asset_type_display()} has been {inquiry.get_status_display()}",
                message=f"Admin action: {inquiry.admin_notes or 'No additional notes provided'}",
                related_object=inquiry
            )
            
            messages.success(request, "Request processed successfully.")
            return redirect('manage_requests')
    else:
        form = AdminRequestActionForm(instance=inquiry)
    
    context = {
        'inquiry': inquiry,
        'form': form,
    }
    return render(request, 'requests/admin/process_request.html', context)