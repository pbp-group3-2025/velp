import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import Report
from .forms import ReportUpdateForm, ReportCreateForm
from django.views.decorators.csrf import csrf_exempt

# If you don't want clients to send content_type at all:
# map target_type -> model class
from main.models import Venue   # adjust imports to your actual apps
from review.models import Review # adjust
from posts.models import Post     # adjust
from community.models import Group  # adjust
from posts.models import Comment
# from comments.models import Comment  # adjust

TARGET_MODEL = {
    "venue": Venue,
    "review": Review,
    "post": Post,
    "community": Group,
    "comment": Comment,
}

def get_json_data(request):
    """Helper to get JSON data from request body or POST"""
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return {}
    return request.POST.dict()

@csrf_exempt
@require_POST
def create_report(request):
    # Manual authentication check to avoid 302 Redirects
    if not request.user.is_authenticated:
        return JsonResponse({
            "ok": False, 
            "message": "You must be logged in to submit a report."
        }, status=401)

    data = get_json_data(request)
    form = ReportCreateForm(data)
    
    if not form.is_valid():
        return JsonResponse({"ok": False, "message": "Invalid form", "errors": form.errors}, status=400)

    target_type = form.cleaned_data["target_type"]
    object_id   = form.cleaned_data["object_id"]
    reason      = form.cleaned_data["reason"]
    details     = form.cleaned_data.get("details", "")

    model_cls = TARGET_MODEL.get(target_type)
    if model_cls is None:
        return JsonResponse({"ok": False, "message": "Invalid target type."}, status=400)
    
    # Handle potential UUID/Value errors during lookup
    try:
        if not model_cls.objects.filter(pk=object_id).exists():
            return JsonResponse({"ok": False, "message": "Target not found."}, status=404)
    except (ValueError, ValidationError):
        return JsonResponse({"ok": False, "message": "Invalid ID format."}, status=400)

    content_type = ContentType.objects.get_for_model(model_cls, for_concrete_model=False)

    with transaction.atomic():
        existing = Report.objects.select_for_update().filter(
            reporter=request.user,
            content_type=content_type,
            object_id=object_id,
            status="open",
        ).first()
        
        if existing:
            return JsonResponse(
                {"ok": False, "message": "You already have an open report for this item.", "existing_id": existing.pk},
                status=409,
            )

        report = Report.objects.create(
            reporter=request.user,
            content_type=content_type,
            object_id=object_id,
            target_type=target_type,
            reason=reason,
            details=details,
            status="open",
        )

    return JsonResponse({"ok": True, "id": report.pk, "message": "Thanks! Your report has been submitted."}, status=201)


@login_required
def my_reports(request):
    qs = Report.objects.filter(reporter=request.user).select_related('reporter', 'handled_by', 'content_type').distinct().order_by('-created_at')
    
    reports_data = []
    for report in qs:
        reports_data.append({
            'id': report.pk,
            'target_type': report.target_type,
            'object_id': report.object_id,
            'reason': report.reason,
            'details': report.details,
            'status': report.status,
            'created_at': report.created_at.isoformat() if report.created_at else None,
            'resolved_at': report.resolved_at.isoformat() if report.resolved_at else None,
            'handled_by': report.handled_by.username if report.handled_by else None,
            'is_locked': report.is_locked,
            'target_name': report.target_name,
        })
    
    return JsonResponse({"ok": True, "reports": reports_data}, status=200)


@login_required
def mod_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"ok": False, "message": "Forbidden"}, status=403)

    qs = (Report.objects
          .select_related("reporter", "handled_by", "content_type")
          .order_by("-created_at"))

    q = request.GET.get("q")
    if q:
        qs = qs.filter(
            Q(details__icontains=q) |
            Q(reporter__username__icontains=q) |
            Q(reason__icontains=q)
        )

    per_page = int(request.GET.get("per_page", 15))
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    reports_data = []
    for report in page_obj:
        reports_data.append({
            'id': report.pk,
            'reporter': report.reporter.username,
            'reporter_id': report.reporter.pk,
            'target_type': report.target_type,
            'object_id': report.object_id,
            'reason': report.reason,
            'details': report.details,
            'status': report.status,
            'created_at': report.created_at.isoformat() if report.created_at else None,
            'resolved_at': report.resolved_at.isoformat() if report.resolved_at else None,
            'handled_by': report.handled_by.username if report.handled_by else None,
            'handled_by_id': report.handled_by.pk if report.handled_by else None,
            'is_locked': report.is_locked,
            'target_name': report.target_name,
        })

    return JsonResponse({
        "ok": True,
        "reports": reports_data,
        "pagination": {
            "page": page_obj.number,
            "per_page": per_page,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }
    }, status=200)


@require_POST
@login_required
def update_report(request, pk: int):
    report = get_object_or_404(Report, pk=pk)

    if report.reporter_id != request.user.id:
        return JsonResponse({"ok": False, "message": "You cannot edit this report."}, status=403)

    if report.is_locked:
        return JsonResponse({"ok": False, "message": "This report can no longer be edited."}, status=409)

    data = get_json_data(request)
    form = ReportUpdateForm(data, instance=report)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    form.save()
    return JsonResponse({"ok": True, "message": "Report updated.", "id": report.id})


@require_POST
@login_required
def update_report_status(request, pk: int):
    if not request.user.is_staff:
        return JsonResponse({"ok": False, "message": "Staff only"}, status=403)

    report = get_object_or_404(Report, pk=pk)
    data = get_json_data(request)
    new_status = data.get('status')

    if new_status not in (Report.Status.RESOLVED, Report.Status.REJECTED, Report.Status.UNDER_REVIEW):
        return JsonResponse({"ok": False, "message": "Invalid status"}, status=400)

    report.set_status(new_status, request.user)
    return JsonResponse({
        "ok": True,
        "message": "Report status updated.",
        "id": report.id,
        "status": report.status,
        "handled_by": request.user.username,
        "resolved_at": report.resolved_at.isoformat() if report.resolved_at else None,
    }, status=200)

@require_POST
@login_required
def delete_report(request, pk: int):   # <-- accept pk
    report = get_object_or_404(Report, pk=pk, reporter=request.user)
    if getattr(report, "is_locked", False):
        return JsonResponse({"ok": False, "message": "Locked reports cannot be deleted."}, status=403)
    report.delete()
    return JsonResponse({"ok": True, "message": "Report deleted.", "id": pk}, status=200)

@login_required
def mod_detail(request, pk: int):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"ok": False, "message": "Forbidden"}, status=403)

    report = get_object_or_404(
        Report.objects.select_related("reporter", "handled_by", "content_type"),
        pk=pk
    )

    target_obj = None
    try:
        if hasattr(report, "target") and report.target:
            target_obj = report.target
    except Exception:
        target_obj = None

    # Derive a human-friendly name from the target object
    target_name = report.target_name

    report_data = {
        'id': report.pk,
        'reporter': {
            'id': report.reporter.pk,
            'username': report.reporter.username,
        },
        'target_type': report.target_type,
        'object_id': report.object_id,
        'target_name': target_name,
        'reason': report.reason,
        'details': report.details,
        'status': report.status,
        'created_at': report.created_at.isoformat() if report.created_at else None,
        'resolved_at': report.resolved_at.isoformat() if report.resolved_at else None,
        'handled_by': {
            'id': report.handled_by.pk,
            'username': report.handled_by.username,
        } if report.handled_by else None,
        'is_locked': report.is_locked,
        'content_type': {
            'id': report.content_type.pk,
            'app_label': report.content_type.app_label,
            'model': report.content_type.model,
        },
    }

    return JsonResponse({"ok": True, "report": report_data}, status=200)


def get_report_options(request):
    """
    Get available options for report forms (target types, reasons, statuses).
    Useful for Flutter to populate dropdowns/selectors.
    """
    return JsonResponse({
        "ok": True,
        "options": {
            "target_types": [
                {"value": choice[0], "label": choice[1]} 
                for choice in Report.TargetType.choices
            ],
            "reasons": [
                {"value": choice[0], "label": choice[1]} 
                for choice in Report.Reason.choices
            ],
            "statuses": [
                {"value": choice[0], "label": choice[1]} 
                for choice in Report.Status.choices
            ],
        }
    }, status=200)
