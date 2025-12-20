from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Group, Post, Comment, Membership
from .forms import PostForm, GroupForm, CommentForm, GroupDescriptionForm
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt  # <-- added

User = get_user_model()

def group_list(request):
    groups = Group.objects.all().order_by('name')
    return render(request, 'group_list.html', {'groups': groups})

def group_detail(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').prefetch_related('comments__author')
    form = PostForm()
    comment_form = CommentForm()   # reusable comment form
    return render(request, 'group_detail.html', {
        'group': group,
        'posts': posts,
        'form': form,
        'comment_form': comment_form,
    })

@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            g = form.save(commit=False)
            g.owner = request.user
            g.save()

            # make sure the creator is a member too
            Membership.objects.get_or_create(group=g, user=request.user)

            if is_ajax(request):
                return JsonResponse({
                    "ok": True,
                    "redirect": reverse("community:group_list")
                })

            return redirect("community:group_list")

        else:
            if is_ajax(request):
                return JsonResponse(
                    {"ok": False, "error": "Invalid form"},
                    status=400
                )
    else:
        form = GroupForm()

    return render(request, "group_form.html", {"form": form})

@login_required
def edit_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if not group.is_owner(request.user):
        return HttpResponseForbidden("Only owner can edit.")

    form = GroupForm(request.POST or None, instance=group)

    if request.method == "POST" and form.is_valid():
        form.save()
        if is_ajax(request):
            return JsonResponse({
                "ok": True,
                "redirect": reverse("community:group_list"),
            })
        return redirect("community:group_list")
    return render(request, "group_edit.html", {
        "form": form,
        "group": group,
    })

@login_required
def delete_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if not group.is_owner(request.user):
        return HttpResponseForbidden("Only the owner can delete this group.")
    if request.method == "POST":
        group.delete()
        if is_ajax(request):
            return JsonResponse({"ok": True, "redirect": reverse("community:group_list")})
        return redirect("community:group_list")
    return render(request, "group_confirm_delete.html", {"group": group})

@login_required
def join_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    Membership.objects.get_or_create(group=group, user=request.user)
    return redirect("community:group_detail", slug=slug)

@login_required
def leave_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if group.is_owner(request.user):
        return HttpResponseForbidden("Owner cannot leave their own group.")
    Membership.objects.filter(group=group, user=request.user).delete()
    return redirect("community:group_list")

@login_required
def create_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.group = group
            post.author = request.user
            post.save()

            if is_ajax(request):
                card_html = render_to_string("post_card.html", {"post": post, "request": request})
                return JsonResponse({"ok": True, "card_html": card_html, "append_to": "#post-grid"})
            return redirect("community:group_detail", slug=group.slug)
        else:
            if is_ajax(request):
                return JsonResponse({"ok": False, "error": "Invalid post form"}, status=400)

    form = PostForm()
    return render(request, "post_form.html", {"form": form, "group": group})

@login_required
def delete_post(request, slug, pk):
    group = get_object_or_404(Group, slug=slug)
    post  = get_object_or_404(Post, pk=pk, group=group)

    if not post.can_delete(request.user):
        return HttpResponseForbidden("You cannot delete this post.")

    if request.method == "POST":
        post.delete()
        if is_ajax(request):
            return JsonResponse({"ok": True})
        return redirect("community:group_detail", slug=slug)

    return render(request, "post_confirm_delete.html", {"group": group, "post": post})

def post_detail(request, slug, pk):
    group = get_object_or_404(Group, slug=slug)
    post = get_object_or_404(
        Post.objects.select_related("author", "group")
            .prefetch_related("comments__author"),
        pk=pk, group=group
    )
    if request.method == "POST" and request.user.is_authenticated:
        content = (request.POST.get("content") or "").strip()
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
        return redirect("community:post_detail", slug=slug, pk=pk)

    return render(request, "post_detail.html", {"group": group, "post": post})

@login_required
def create_comment(request, slug, pk):
    post = get_object_or_404(Post, pk=pk, group__slug=slug)
    if request.method != 'POST':
        return redirect('community:group_detail', slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = post
        c.author = request.user 
        c.save()
    return redirect('community:group_detail', slug=slug)

@login_required
def delete_comment(request, slug, pk, cpk):
    post = get_object_or_404(Post, pk=pk, group__slug=slug)
    comment = get_object_or_404(Comment, pk=cpk, post=post)
    if not (request.user.id == comment.author_id or request.user.id == post.group.owner_id):
        return HttpResponseForbidden("You cannot delete this comment.")
    if request.method == "POST":
        comment.delete()
        if is_ajax(request):
            return JsonResponse({"ok": True})
        return redirect("community:post_detail", slug=slug, pk=pk)
    return render(request, "comment_confirm_delete.html", {"post": post, "comment": comment})

def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

# ---------- JSON / Flutter API ----------

def _serialize_user(user):
    if user is None:
        return None
    return {
        "id": user.id,
        "username": user.username,
    }

def _serialize_group(group):
    return {
        "id": group.id,
        "name": group.name,
        "slug": group.slug,
        "description": group.description,
        "owner": _serialize_user(group.owner),
    }

def _serialize_comment(comment):
    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
        "author": _serialize_user(comment.author),
    }

def _serialize_post(post, include_comments=False):
    data = {
        "id": post.id,
        "headline": post.headline,
        "content": post.content,
        "image_url": post.image_url,
        "created_at": post.created_at.isoformat(),
        "author": _serialize_user(post.author),
        "group_id": post.group_id,
    }
    if include_comments:
        data["comments"] = [_serialize_comment(c) for c in post.comments.all()]
    return data

@require_GET
def api_group_list(request):
    groups = Group.objects.select_related("owner").all().order_by("name")
    return JsonResponse({
        "ok": True,
        "groups": [_serialize_group(g) for g in groups],
    })

@require_GET
def api_group_detail(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("author") \
                       .prefetch_related("comments__author") \
                       .all()

    return JsonResponse({
        "ok": True,
        "group": _serialize_group(group),
        "posts": [
            _serialize_post(p, include_comments=True) for p in posts
        ],
    })

@csrf_exempt
@login_required
@require_POST
def api_create_group(request):
    form = GroupForm(request.POST)
    if not form.is_valid():
        errors = {field: list(err_list) for field, err_list in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    g = form.save(commit=False)
    g.owner = request.user
    g.save()

    Membership.objects.get_or_create(group=g, user=request.user)

    return JsonResponse({
        "ok": True,
        "group": _serialize_group(g),
    }, status=201)

@csrf_exempt
@login_required
@require_POST
def api_edit_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if not group.is_owner(request.user):
        return JsonResponse(
            {"ok": False, "error": "Only owner can edit."},
            status=403,
        )

    form = GroupForm(request.POST, instance=group)
    if not form.is_valid():
        errors = {field: list(err_list) for field, err_list in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    form.save()
    return JsonResponse({
        "ok": True,
        "group": _serialize_group(group),
    })

@csrf_exempt
@login_required
@require_POST
def api_delete_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if not group.is_owner(request.user):
        return JsonResponse(
            {"ok": False, "error": "Only owner can delete this group."},
            status=403,
        )

    group.delete()
    return JsonResponse({"ok": True})

@csrf_exempt
@login_required
@require_POST
def api_join_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    Membership.objects.get_or_create(group=group, user=request.user)
    return JsonResponse({"ok": True})

@csrf_exempt
@login_required
@require_POST
def api_leave_group(request, slug):
    group = get_object_or_404(Group, slug=slug)

    if group.is_owner(request.user):
        return JsonResponse(
            {"ok": False, "error": "Owner cannot leave their own group."},
            status=403,
        )

    Membership.objects.filter(group=group, user=request.user).delete()
    return JsonResponse({"ok": True})

@csrf_exempt
@login_required
@require_POST
def api_create_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    form = PostForm(request.POST)
    if not form.is_valid():
        errors = {field: list(err_list) for field, err_list in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    post = form.save(commit=False)
    post.group = group
    post.author = request.user
    post.save()

    return JsonResponse({
        "ok": True,
        "post": _serialize_post(post, include_comments=True),
    }, status=201)

@require_GET
def api_post_detail(request, slug, pk):
    group = get_object_or_404(Group, slug=slug)
    post = get_object_or_404(
        Post.objects.select_related("author", "group")
            .prefetch_related("comments__author"),
        pk=pk,
        group=group,
    )
    return JsonResponse({
        "ok": True,
        "group": _serialize_group(group),
        "post": _serialize_post(post, include_comments=True),
    })

@csrf_exempt
@login_required
@require_POST
def api_delete_post(request, slug, pk):
    group = get_object_or_404(Group, slug=slug)
    post = get_object_or_404(Post, pk=pk, group=group)

    if not post.can_delete(request.user):
        return JsonResponse(
            {"ok": False, "error": "You cannot delete this post."},
            status=403,
        )

    post.delete()
    return JsonResponse({"ok": True})

@csrf_exempt
@login_required
@require_POST
def api_create_comment(request, slug, pk):
    post = get_object_or_404(Post, pk=pk, group__slug=slug)
    form = CommentForm(request.POST)
    if not form.is_valid():
        errors = {field: list(err_list) for field, err_list in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    c = form.save(commit=False)
    c.post = post
    c.author = request.user
    c.save()

    return JsonResponse({
        "ok": True,
        "comment": _serialize_comment(c),
    }, status=201)

@csrf_exempt
@login_required
@require_POST
def api_delete_comment(request, slug, pk, cpk):
    post = get_object_or_404(Post, pk=pk, group__slug=slug)
    comment = get_object_or_404(Comment, pk=cpk, post=post)

    if not (request.user.id == comment.author_id or request.user.id == post.group.owner_id):
        return JsonResponse(
            {"ok": False, "error": "You cannot delete this comment."},
            status=403,
        )

    comment.delete()
    return JsonResponse({"ok": True})
