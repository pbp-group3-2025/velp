from django.shortcuts import render, redirect, get_object_or_404
from urllib3 import request
from main.forms import VenueForm
from main.models import Venue
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
        venue_list = Venue.objects.all()
    else:
        venue_list = Venue.objects.filter(user=request.user)


    context = {
        'npm' : '2406365370',
        'name': request.user.username,
        'class': 'PBP KKI',
        'venue_list': venue_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }


    return render(request, "main.html", context)


def create_venue(request):
    form = VenueForm(request.POST or None)


    if form.is_valid() and request.method == 'POST':
        venue_entry = form.save(commit = False)
        venue_entry.user = request.user
        venue_entry.save()
        return redirect('main:show_main')


    context = {
        'form': form
    }


    return render(request, "create_venue.html", context)


@login_required(login_url='/login')
def show_venue(request, id):
    venue = get_object_or_404(Venue, pk=id)


    context = {
        "venue": venue
    }


    return render(request, "venue_detail.html", context)


def show_xml(request):
    venue_list = Venue.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")


def show_json(request):
    venue_list = Venue.objects.all()
    json_data = serializers.serialize("json", venue_list)
    return HttpResponse(json_data, content_type="application/json")


def show_xml_by_id(request, venue_id):
    try:
        venue_item = Venue.objects.filter(pk=venue_id)
        xml_data = serializers.serialize("xml", venue_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Venue.DoesNotExist:
        return HttpResponse(status=404)


def show_json_by_id(request, venue_id):
    data = Venue.objects.filter(pk=venue_id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


def show_json_by_id(request, venue_id):
    try:
        venue_item = Venue.objects.get(pk=venue_id)
        json_data = serializers.serialize("json", [venue_item])
        return HttpResponse(json_data, content_type="application/json")
    except Venue.DoesNotExist:
        return HttpResponse(status=404)
   
def register(request):
    form = UserCreationForm()


    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)


def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)


      if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response


   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response


def edit_venue(request, id):
    venue = get_object_or_404(Venue, pk=id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('main:show_main')


    context = {
        'form': form
    }


    return render(request, "edit_venue.html", context)


def delete_venue(request, id):
    venue = get_object_or_404(Venue, pk=id)
    venue.delete()
    return HttpResponseRedirect(reverse('main:show_main'))

