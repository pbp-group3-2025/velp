from django.shortcuts import render

# Create your views here.
# reports/views.py
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from .models import Report
from .forms import ReportUpdateForm, ReportCreateForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType


TARGET_MODEL = {
    "venue": Venue,
    "review": Review,
    "post": Post,
    "comment": Comment,
}

# main/views.py

@require_POST
@login_required
def create_report(request):
    form = ReportCreateForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    target_type = form.cleaned_data["target_type"]
    object_id   = form.cleaned_data["object_id"]
    reason      = form.cleaned_data["reason"]
    details     = form.cleaned_data.get("details", "")

    app_model = TARGET_MODEL.get(target_type)
    if not app_model:
        return JsonResponse({"ok": False, "message": "Invalid target type."}, status=400)

    from django.apps import apps
    model_cls = apps.get_model(*app_model)
    obj = model_cls.objects.filter(pk=object_id).first()
    if not obj:
        return JsonResponse({"ok": False, "message": "Target not found."}, status=404)

    from django.contrib.contenttypes.models import ContentType
    ct = ContentType.objects.get_for_model(model_cls)

    # resolve name directly here (no utils file)
    if hasattr(obj, "name"):
        target_name = str(obj.name)
    elif hasattr(obj, "title"):
        target_name = str(obj.title)
    elif hasattr(obj, "username"):
        target_name = str(obj.username)
    else:
        target_name = str(obj)

    if Report.objects.filter(
        reporter=request.user, content_type=ct, object_id=object_id, status=Report.Status.OPEN
    ).exists():
        return JsonResponse({"ok": False, "message": "You already have an open report for this item."}, status=409)

    report = Report(
        reporter=request.user,
        content_type=ct,
        object_id=object_id,
        target_type=target_type,
        reason=reason,
        details=details,
        target_name=target_name,  # 👈 store the snapshot name here
    )
    report.save()

    return JsonResponse({"ok": True, "message": "Thanks! Your report has been submitted.", "id": report.id}, status=201)

@require_POST
@login_required
def update_report(request, pk: int):
    report = get_object_or_404(Report, pk=pk)

    # Only the original reporter can edit
    if report.reporter_id != request.user.id:
        return HttpResponseForbidden("You cannot edit this report.")

    # Block edits if locked (resolved/rejected)
    if report.is_locked:
        return JsonResponse(
            {"ok": False, "message": "This report can no longer be edited."},
            status=409
        )

    form = ReportUpdateForm(request.POST, instance=report)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    form.save()  # keep current status (OPEN/UNDER_REVIEW) unchanged
    return JsonResponse({"ok": True, "message": "Report updated.", "id": report.id})

@login_required
@require_POST
def update_report_status(request, pk: int):
    """Update report status (staff only)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Staff only")
        
    report = get_object_or_404(Report, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status not in [Report.Status.RESOLVED, Report.Status.REJECTED]:
        return HttpResponseBadRequest("Invalid status")
        
    report.set_status(new_status, request.user)
    return redirect('main:mod_list')
