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


@require_POST
@login_required
def create_report(request):
    form = ReportCreateForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    # For demo: skip existence check if target type is post/comment
    if form.cleaned_data["target_type"] not in ["post", "comment"]:
        # sanity: target must exist (for non-demo items)
        model_cls = form.cleaned_data["content_type"].model_class()
        if not model_cls.objects.filter(pk=form.cleaned_data["object_id"]).exists():
            return JsonResponse({"ok": False, "message": "Target not found."}, status=404)

    # optional: avoid duplicates (open report by same user on same target)
    exists = Report.objects.filter(
        reporter=request.user,
        content_type=form.cleaned_data["content_type"],
        object_id=form.cleaned_data["object_id"],
        status=Report.Status.OPEN,
    ).exists()
    if exists:
        return JsonResponse({"ok": False, "message": "You already have an open report for this item."}, status=409)

    report = form.save(commit=False)
    report.reporter = request.user
    report.save()
    return JsonResponse({"ok": True, "message": "Thanks! Your report has been submitted.", "id": report.id}, status=201)


@login_required
def my_reports(request):
    """Show reports created by the current user with simple edit links."""
    qs = Report.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, '/my_reports.html', {'reports': qs})

# (Optional) simple list for moderators; add your own permission checks as needed
@login_required
def moderation_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseBadRequest("Forbidden")
    qs = Report.objects.select_related("reporter", "handled_by").order_by("-created_at")
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(details__icontains=q) | Q(reporter__username__icontains=q))
    page_obj = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, "/mod_list.html", {"page_obj": page_obj, "Report": Report})

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
