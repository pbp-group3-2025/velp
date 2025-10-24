from django.shortcuts import render, redirect, get_object_or_404
from review.forms import ReviewForm
from review.models import Review
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
        review_list = Review.objects.all()
    else:
        review_list = Review.objects.filter(user=request.user)

    context = {
        'npm' : '2406365370',
        'name': request.user.username,
        'class': 'PBP KKI',
        'review_list': review_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }

    return render(request, "review/main.html", context)


def create_review(request):
    form = ReviewForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        review_entry = form.save(commit = False)
        review_entry.user = request.user
        review_entry.save()
        return redirect('review:main')

    context = {
        'form': form
    }

    return render(request, "review/create_review.html", context)


@login_required(login_url='/login')
def show_review(request, id):
    review = get_object_or_404(Review, pk=id)

    context = {
        "review": review
    }

    return render(request, "review/review_detail.html", context)


def show_xml(request):
    venue_list = Review.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")


def show_json(request):
    venue_list = Review.objects.all()
    json_data = serializers.serialize("json", venue_list)
    return HttpResponse(json_data, content_type="application/json")


def show_xml_by_id(request, venue_id):
    try:
        venue_item = Review.objects.filter(pk=venue_id)
        xml_data = serializers.serialize("xml", venue_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Review.DoesNotExist:
        return HttpResponse(status=404)


def show_json_by_id(request, venue_id):
    data = Review.objects.filter(pk=venue_id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


def show_json_by_id(request, venue_id):
    try:
        venue_item = Review.objects.get(pk=venue_id)
        json_data = serializers.serialize("json", [venue_item])
        return HttpResponse(json_data, content_type="application/json")
    except Review.DoesNotExist:
        return HttpResponse(status=404)
   
def edit_review(request, id):
    review = get_object_or_404(Review, pk=id)
    form = ReviewForm(request.POST or None, instance=review)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('review:main')

    context = {
        'form': form
    }

    return render(request, "review/edit_review.html", context)


def delete_review(request, id):
    review = get_object_or_404(Review, pk=id)
    review.delete()
    return HttpResponseRedirect(reverse('review:main'))
