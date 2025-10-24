from django.shortcuts import render, redirect, get_object_or_404
from community.forms import CommunityForm
from community.models import Community
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
        community_list = Community.objects.all()
    else:
        community_list = Community.objects.filter(user=request.user)

    context = {
        'npm' : '2406365370',
        'name': request.user.username,
        'class': 'PBP KKI',
        'community_list': community_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }

    return render(request, "community/main.html", context)


def create_community(request):
    form = CommunityForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        community_entry = form.save(commit = False)
        community_entry.user = request.user
        community_entry.save()
        return redirect('community:main')

    context = {
        'form': form
    }

    return render(request, "community/create_community.html", context)


@login_required(login_url='/login')
def show_community(request, id):
    community = get_object_or_404(Community, pk=id)

    context = {
        "community": community
    }

    return render(request, "community/community_detail.html", context)


def show_xml(request):
    venue_list = Community.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")


def show_json(request):
    venue_list = Community.objects.all()
    json_data = serializers.serialize("json", venue_list)
    return HttpResponse(json_data, content_type="application/json")


def show_xml_by_id(request, venue_id):
    try:
        venue_item = Community.objects.filter(pk=venue_id)
        xml_data = serializers.serialize("xml", venue_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Community.DoesNotExist:
        return HttpResponse(status=404)


def show_json_by_id(request, venue_id):
    data = Community.objects.filter(pk=venue_id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


def show_json_by_id(request, venue_id):
    try:
        venue_item = Community.objects.get(pk=venue_id)
        json_data = serializers.serialize("json", [venue_item])
        return HttpResponse(json_data, content_type="application/json")
    except Community.DoesNotExist:
        return HttpResponse(status=404)
   
def edit_community(request, id):
    community = get_object_or_404(Community, pk=id)
    form = CommunityForm(request.POST or None, instance=community)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('community:main')

    context = {
        'form': form
    }

    return render(request, "community/edit_community.html", context)


def delete_community(request, id):
    community = get_object_or_404(Community, pk=id)
    community.delete()
    return HttpResponseRedirect(reverse('community:main'))
