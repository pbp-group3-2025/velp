from django.shortcuts import render, redirect, get_object_or_404
from main.forms import VenueForm, BookingForm
from main.models import Venue, Booking
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
from django import forms
from django.utils import timezone
from datetime import time, timedelta, date
from django.core.exceptions import ValidationError


# Create your views here.
@login_required(login_url='/login')
def show_main(request):

    venue_list = Venue.objects.all() 
    
    # Get filter, default is 'all'
    filter_type = request.GET.get("filter", "all") 
    
    valid_filters = ['pitch', 'stadium', 'sports_centre']
    if filter_type in valid_filters:
        venue_list = venue_list.filter(leisure=filter_type) 
    
    venue_list = venue_list.order_by('name')

    context = {
        'name': request.user.username,
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

def create_booking(request, id):
    venue = get_object_or_404(Venue, pk=id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # extract form cleaned data
            start_hour = int(form.cleaned_data['start_hour'])
            duration = int(form.cleaned_data['duration_hours'])
            d = form.cleaned_data['date']

            # check collisions for each hour: start_hour .. start_hour+duration-1
            blocked = []
            for h in range(start_hour, start_hour + duration):
                hh = h % 24
                t = time(hour=hh, minute=0)
                if Booking.objects.filter(venue=venue, date=d, start_time=t).exists():
                    blocked.append(hh)

            if blocked:
                slots = ", ".join(f"{h:02d}:00-{(h+1)%24:02d}:00" for h in blocked)
                form.add_error(None, f"These hour slots are already booked for {d}: {slots}. Pick other hours.")
            else:
                # create booking
                booking = form.save(venue=venue, user=request.user, commit=True)
                # compute and ensure total_price saved (save() of Booking handles it)
                booking.total_price = booking.compute_total_price()
                booking.save()
                messages.success(request, "Booking created successfully.")
                return redirect(reverse('main:booking_list'))
    else:
        # GET: initial form
        initial = {'date': date.today()}
        form = BookingForm(initial=initial)

    return render(request, "booking/booking_form.html", {"form": form, "venue": venue})

@login_required(login_url='/login')
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date', 'start_time')
    return render(request, "booking/booking_list.html", {"bookings": bookings})


@login_required(login_url='/login')
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, "booking/booking_confirm.html", {"booking": booking})


@login_required(login_url='/login')
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        booking.status = "CANCELLED"
        booking.save()
        messages.success(request, "Booking cancelled.")
        return redirect(reverse('main:booking_list'))
    return render(request, "booking/booking_cancel_confirm.html", {"booking": booking})
