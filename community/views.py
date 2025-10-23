# community/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Group, Post, Comment
from .forms import PostForm, GroupForm, CommentForm, GroupDescriptionForm

User = get_user_model()

def _guest_user():
    # For dev only: create or fetch a "guest" user so posts/comments can be created without login
    guest, _ = User.objects.get_or_create(username='guest', defaults={'password': '!'})  # unusable password
    return guest

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

def create_group(request):
    """Dev mode: allow anyone to create a group."""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()  # slug auto-generates in model.save()
            return redirect('community:group_detail', slug=group.slug)
    else:
        form = GroupForm()
    return render(request, 'group_form.html', {'form': form})

def edit_group(request, slug):
    """Edit group description (dev mode: no auth)."""
    group = get_object_or_404(Group, slug=slug)
    if request.method == 'POST':
        form = GroupDescriptionForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('community:group_detail', slug=group.slug)
    else:
        form = GroupDescriptionForm(instance=group)
    return render(request, 'group_edit.html', {'group': group, 'form': form})

def delete_group(request, slug):
    """Delete a group (dev mode: no auth)."""
    group = get_object_or_404(Group, slug=slug)
    if request.method == 'POST':
        group.delete()  # cascades to posts
        return redirect('community:group_list')
    posts_count = group.posts.count()
    return render(request, 'group_confirm_delete.html', {'group': group, 'posts_count': posts_count})


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
            return redirect("community:group_detail", slug=group.slug)
    else:
        form = PostForm()

    return render(request, "post_form.html", {"form": form, "group": group})


def delete_post(request, slug, pk):
    """Delete a post inside a group and return to the group detail page."""
    post = get_object_or_404(Post, pk=pk, group__slug=slug)
    if request.method == 'POST':
        post.delete()
        return redirect('community:group_detail', slug=slug)
    # optional: confirm page if accessed by GET
    return render(request, 'post_confirm_delete.html', {'group': post.group, 'post': post})

def post_detail(request, slug, pk):
    group = get_object_or_404(Group, slug=slug)
    post = get_object_or_404(
        Post.objects.select_related("author", "group")
            .prefetch_related("comments__author"),
        pk=pk, group=group
    )

    # Optional: simple inline comment create on the detail page
    if request.method == "POST" and request.user.is_authenticated:
        content = (request.POST.get("content") or "").strip()
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
        return redirect("community:post_detail", slug=slug, pk=pk)

    return render(request, "post_detail.html", {"group": group, "post": post})

def create_comment(request, slug, pk):
    post = get_object_or_404(Post, pk=pk, group__slug=slug)
    if request.method != 'POST':
        return redirect('community:group_detail', slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = post
        c.author = request.user if request.user.is_authenticated else _guest_user()
        c.save()
    return redirect('community:group_detail', slug=slug)
