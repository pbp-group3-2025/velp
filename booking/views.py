from django.shortcuts import render, redirect, get_object_or_404
from booking.forms import BookingForm
from booking.models import Booking
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
        booking_list = Booking.objects.all()
    else:
        booking_list = Booking.objects.filter(user=request.user)

    context = {
        'npm' : '2406365370',
        'name': request.user.username,
        'class': 'PBP KKI',
        'booking_list': booking_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }

    return render(request, "booking/main.html", context)


def create_booking(request):
    form = BookingForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        booking_entry = form.save(commit = False)
        booking_entry.user = request.user
        booking_entry.save()
        return redirect('booking:main')

    context = {
        'form': form
    }

    return render(request, "booking/create_booking.html", context)


@login_required(login_url='/login')
def show_booking(request, id):
    booking = get_object_or_404(Booking, pk=id)

    context = {
        "booking": booking
    }

    return render(request, "booking/booking_detail.html", context)


def show_xml(request):
    venue_list = Booking.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")


def show_json(request):
    venue_list = Booking.objects.all()
    json_data = serializers.serialize("json", venue_list)
    return HttpResponse(json_data, content_type="application/json")


def show_xml_by_id(request, venue_id):
    try:
        venue_item = Booking.objects.filter(pk=venue_id)
        xml_data = serializers.serialize("xml", venue_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Booking.DoesNotExist:
        return HttpResponse(status=404)


def show_json_by_id(request, venue_id):
    data = Booking.objects.filter(pk=venue_id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


def show_json_by_id(request, venue_id):
    try:
        venue_item = Booking.objects.get(pk=venue_id)
        json_data = serializers.serialize("json", [venue_item])
        return HttpResponse(json_data, content_type="application/json")
    except Booking.DoesNotExist:
        return HttpResponse(status=404)
   
def edit_booking(request, id):
    booking = get_object_or_404(Booking, pk=id)
    form = BookingForm(request.POST or None, instance=booking)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('booking:main')

    context = {
        'form': form
    }

    return render(request, "booking/edit_booking.html", context)


def delete_booking(request, id):
    booking = get_object_or_404(Booking, pk=id)
    booking.delete()
    return HttpResponseRedirect(reverse('booking:main'))
