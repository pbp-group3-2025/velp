from django.shortcuts import render, redirect, get_object_or_404
from post.forms import PostForm
from post.models import Post
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
        post_list = Post.objects.all()
    else:
        post_list = Post.objects.filter(user=request.user)

    context = {
        'npm' : '2406365370',
        'name': request.user.username,
        'class': 'PBP KKI',
        'post_list': post_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }

    return render(request, "post/main.html", context)


def create_post(request):
    form = PostForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        post_entry = form.save(commit = False)
        post_entry.user = request.user
        post_entry.save()
        return redirect('post:main')

    context = {
        'form': form
    }

    return render(request, "post/create_post.html", context)


@login_required(login_url='/login')
def show_post(request, id):
    post = get_object_or_404(Post, pk=id)

    context = {
        "post": post
    }

    return render(request, "post/post_detail.html", context)


def show_xml(request):
    venue_list = Post.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")


def show_json(request):
    venue_list = Post.objects.all()
    json_data = serializers.serialize("json", venue_list)
    return HttpResponse(json_data, content_type="application/json")


def show_xml_by_id(request, venue_id):
    try:
        venue_item = Post.objects.filter(pk=venue_id)
        xml_data = serializers.serialize("xml", venue_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Post.DoesNotExist:
        return HttpResponse(status=404)


def show_json_by_id(request, venue_id):
    data = Post.objects.filter(pk=venue_id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")


def show_json_by_id(request, venue_id):
    try:
        venue_item = Post.objects.get(pk=venue_id)
        json_data = serializers.serialize("json", [venue_item])
        return HttpResponse(json_data, content_type="application/json")
    except Post.DoesNotExist:
        return HttpResponse(status=404)
   
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('post:main')

    context = {
        'form': form
    }

    return render(request, "post/edit_post.html", context)


def delete_post(request, id):
    post = get_object_or_404(Post, pk=id)
    post.delete()
    return HttpResponseRedirect(reverse('post:main'))
