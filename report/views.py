from django.shortcuts import render, redirect, get_object_or_404
from report.forms import ReportForm
from report.models import Report
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.
@login_required(login_url='/login')
def show_main(request):

    filter_type = request.GET.get("filter", "all")  # default 'all'

    if filter_type == "all":
        report_list = Report.objects.all()
    else:
        report_list = Report.objects.filter(user=request.user)

    context = {
        'npm' : '2406365370',
        'name': request.user.username,
        'class': 'PBP KKI',
        'report_list': report_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }

    return render(request, "report/main.html", context)


def create_report(request):
    form = ReportForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        report_entry = form.save(commit = False)
        report_entry.user = request.user
        report_entry.save()
        return redirect('report:main')

    context = {
        'form': form
    }

    return render(request, "report/create_report.html", context)


@login_required(login_url='/login')
def show_report(request, id):
    report = get_object_or_404(Report, pk=id)

    context = {
        "report": report
    }

    return render(request, "report/report_detail.html", context)


def show_xml(request):
    venue_list = Report.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")


def show_json(request):
    venue_list = Report.objects.all()
    json_data = serializers.serialize("json", venue_list)
    return HttpResponse(json_data, content_type="application/json")


def show_xml_by_id(request, venue_id):
    try:
        venue_item = Report.objects.filter(pk=venue_id)
        xml_data = serializers.serialize("xml", venue_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Report.DoesNotExist:
        return HttpResponse(status=404)


def show_json_by_id(request, venue_id):
    data = Report.objects.filter(pk=venue_id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


def show_json_by_id(request, venue_id):
    try:
        venue_item = Report.objects.get(pk=venue_id)
        json_data = serializers.serialize("json", [venue_item])
        return HttpResponse(json_data, content_type="application/json")
    except Report.DoesNotExist:
        return HttpResponse(status=404)
   
def edit_report(request, id):
    report = get_object_or_404(Report, pk=id)
    form = ReportForm(request.POST or None, instance=report)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('report:main')

    context = {
        'form': form
    }

    return render(request, "report/edit_report.html", context)


def delete_report(request, id):
    report = get_object_or_404(Report, pk=id)
    report.delete()
    return HttpResponseRedirect(reverse('report:main'))
