import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import Report
from .forms import ReportUpdateForm, ReportCreateForm

# Model imports
from main.models import Venue 
from review.models import Review 
from posts.models import Post 
from community.models import Group 
from posts.models import Comment

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
@login_required
def create_report(request):
    """Handles report creation"""
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
    
    try:
        if not model_cls.objects.filter(pk=object_id).exists():
            return JsonResponse({"ok": False, "message": "Target not found."}, status=404)
    except Exception:
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
            return JsonResponse({"ok": False, "message": "You already have an open report."}, status=409)

        report = Report.objects.create(
            reporter=request.user,
            content_type=content_type,
            object_id=object_id,
            target_type=target_type,
            reason=reason,
            details=details,
            status="open",
        )

    return JsonResponse({"ok": True, "message": "Report submitted."}, status=201)

@csrf_exempt
@login_required
def my_reports(request):
    """Displays history for the logged-in user"""
    qs = Report.objects.filter(reporter=request.user).select_related('reporter', 'handled_by', 'content_type').order_by('-created_at')
    reports_data = [{
        'id': r.pk, 'target_type': r.target_type, 'object_id': r.object_id,
        'reason': r.reason, 'details': r.details, 'status': r.status,
        'is_locked': r.is_locked, 'target_name': r.target_name,
    } for r in qs]
    return JsonResponse({"ok": True, "reports": reports_data})

@csrf_exempt
@login_required
def mod_list(request):
    """Admin dashboard list"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"ok": False, "message": "Forbidden"}, status=403)
    
    qs = Report.objects.select_related("reporter", "handled_by", "content_type").order_by("-created_at")
    reports_data = [{
        'id': r.pk, 'reporter': r.reporter.username, 'target_type': r.target_type,
        'reason': r.reason, 'details': r.details, 'status': r.status,
        'target_name': r.target_name, 'is_locked': r.is_locked,
    } for r in qs]
    return JsonResponse({"ok": True, "reports": reports_data})

@csrf_exempt
@require_POST
@login_required
def update_report(request, pk: int):
    """Updates report details for owner"""
    report = get_object_or_404(Report, pk=pk)
    if report.reporter_id != request.user.id or report.is_locked:
        return JsonResponse({"ok": False, "message": "Forbidden or Locked."}, status=403)

    data = get_json_data(request)
    new_details = data.get('details')
    if new_details is not None:
        report.details = new_details
        report.save()
        return JsonResponse({"ok": True, "message": "Details updated."})
    return JsonResponse({"ok": False, "message": "No data."}, status=400)

@csrf_exempt
@require_POST
@login_required
def update_report_status(request, pk: int):
    """Allows staff to change report status"""
    if not request.user.is_staff:
        return JsonResponse({"ok": False, "message": "Staff only"}, status=403)

    report = get_object_or_404(Report, pk=pk)
    data = get_json_data(request)
    new_status = data.get('status')

    if new_status in [choice[0] for choice in Report.Status.choices]:
        report.set_status(new_status, request.user)
        return JsonResponse({"ok": True, "message": "Status updated."})
    return JsonResponse({"ok": False, "message": "Invalid status"}, status=400)

@csrf_exempt
@require_POST
@login_required
def delete_report(request, pk: int):
    """Deletes report if not locked"""
    report = get_object_or_404(Report, pk=pk, reporter=request.user)
    if report.is_locked:
        return JsonResponse({"ok": False, "message": "Locked."}, status=403)
    report.delete()
    return JsonResponse({"ok": True, "message": "Deleted."})

@csrf_exempt
@login_required
def mod_detail(request, pk: int):
    """Detailed view for staff"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"ok": False, "message": "Forbidden"}, status=403)
    
    report = get_object_or_404(Report.objects.select_related("reporter", "handled_by"), pk=pk)
    report_data = {
        'id': report.pk, 'target_name': report.target_name, 'reason': report.reason,
        'details': report.details, 'status': report.status, 'is_locked': report.is_locked,
    }
    return JsonResponse({"ok": True, "report": report_data})

@csrf_exempt
@login_required
def get_report_options(request):
    """Options for Flutter dropdowns"""
    return JsonResponse({
        "ok": True,
        "options": {
            "target_types": [{"value": c[0], "label": c[1]} for c in Report.TargetType.choices],
            "reasons": [{"value": c[0], "label": c[1]} for c in Report.Reason.choices],
            "statuses": [{"value": c[0], "label": c[1]} for c in Report.Status.choices],
        }
    })