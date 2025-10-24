from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType

from .models import Report
from .forms import ReportUpdateForm, ReportCreateForm

# If you don't want clients to send content_type at all:
# map target_type -> model class
from main.models import Venue   # adjust imports to your actual apps
from review.models import Review # adjust
from posts.models import Post     # adjust
# from comments.models import Comment  # adjust

TARGET_MODEL = {
    "venue": Venue,
    "review": Review,
    "post": Post,
    "comment": Comment,
}

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

    # Resolve model & content type on the server
    model_cls = TARGET_MODEL.get(target_type)
    if model_cls is None:
        return JsonResponse({"ok": False, "message": "Invalid target type."}, status=400)

    # Ensure target exists
    if not model_cls.objects.filter(pk=object_id).exists():
        return JsonResponse({"ok": False, "message": "Target not found."}, status=404)

    content_type = ContentType.objects.get_for_model(model_cls)

    # Avoid duplicate OPEN report by same user on same target
    if Report.objects.filter(
        reporter=request.user,
        content_type=content_type,
        object_id=object_id,
        status=Report.Status.OPEN,
    ).exists():
        return JsonResponse({"ok": False, "message": "You already have an open report for this item."}, status=409)

    report = Report(
        reporter=request.user,
        content_type=content_type,
        object_id=object_id,
        target_type=target_type,
        reason=reason,
        details=details,
    )
    report.save()
    return JsonResponse({"ok": True, "message": "Thanks! Your report has been submitted.", "id": report.id}, status=201)


@login_required
def my_reports(request):
    qs = Report.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'reports/my_reports.html', {'reports': qs})  # <-- no leading slash


@login_required
def mod_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("Forbidden")  # <-- correct response

    qs = Report.objects.select_related("reporter", "handled_by").order_by("-created_at")
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(details__icontains=q) | Q(reporter__username__icontains=q))
    page_obj = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, 'reports/mod_list.html', {"page_obj": page_obj, "Report": Report})


@require_POST
@login_required
def update_report(request, pk: int):
    report = get_object_or_404(Report, pk=pk)

    if report.reporter_id != request.user.id:
        return HttpResponseForbidden("You cannot edit this report.")

    if report.is_locked:
        return JsonResponse({"ok": False, "message": "This report can no longer be edited."}, status=409)

    form = ReportUpdateForm(request.POST, instance=report)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    form.save()
    return JsonResponse({"ok": True, "message": "Report updated.", "id": report.id})


@require_POST
@login_required
def update_report_status(request, pk: int):
    if not request.user.is_staff:
        return HttpResponseForbidden("Staff only")

    report = get_object_or_404(Report, pk=pk)
    new_status = request.POST.get('status')

    if new_status not in (Report.Status.RESOLVED, Report.Status.REJECTED, Report.Status.UNDER_REVIEW):
        return HttpResponseBadRequest("Invalid status")

    report.set_status(new_status, request.user)
    return redirect('reports:mod_list')  # <-- fixed namespace
