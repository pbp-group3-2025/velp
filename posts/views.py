from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.template.loader import render_to_string

from .models import Post, Comment
from .forms import PostForm, CommentForm


@login_required
def post_list(request):
    q = (request.GET.get("q") or "").strip()
    
    qs = (
        Post.objects.select_related("author")
        .order_by("-created_at")
    )
    if q:
        qs = qs.filter(Q(content__icontains=q) | Q(venue_hint__icontains=q))

    page_str = request.GET.get("page") or "1"
    try:
        page_num = int(page_str)
    except ValueError:
        page_num = 1

    page_obj = Paginator(qs, 10).get_page(page_num)
    return render(request, "list.html", {"page_obj": page_obj, "q": q})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'detail.html', {'post': post, 'comment_form': CommentForm()})


@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("Only the author can edit this post.")
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:detail', pk=pk)
    return render(request, 'form.html', {'form': form, 'title': 'Edit Post'})


@login_required
@require_POST
def post_delete(request, pk):
    """Page-level delete (POST-only) then redirect back to list."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("Only the author can delete this post.")
    post.delete()
    return HttpResponseRedirect('/posts/')

@login_required
def api_post_list(request):
    q = (request.GET.get('q') or '').strip()
    qs = Post.objects.select_related('author').annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True),
    ).order_by('-created_at')

    if q:
        qs = qs.filter(Q(content__icontains=q) | Q(venue_hint__icontains=q))

    data = []
    uid = request.user.id
    for p in qs[:50]:
        data.append({
            'id': str(p.id),
            'author': p.author.username,
            'content': p.content,
            'venue_hint': p.venue_hint,
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': p.updated_at.strftime('%Y-%m-%d %H:%M'),
            'like_count': p.like_count,
            'comment_count': p.comment_count,
            'is_liked': p.likes.filter(id=uid).exists(),
            'is_owner': p.author_id == uid,
        })
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def api_post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return JsonResponse({'detail': 'FORBIDDEN'}, status=403)
    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()
        html = render_to_string("partials/card.html", {"p": post, "user": request.user})
        return JsonResponse({'detail': 'UPDATED', 'html': html})
    return JsonResponse({'detail': form.errors.as_json()}, status=400)


@login_required
@require_POST
def api_post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return JsonResponse({'detail': 'FORBIDDEN'}, status=403)
    post.delete()
    return JsonResponse({'detail': 'DELETED'})


@login_required
@require_POST
def api_like_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()})


@login_required
@require_POST
def api_comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = post
        c.author = request.user
        c.save()
        return JsonResponse({
            'detail': 'CREATED',
            'id': str(c.id),
            'author': request.user.username,
            'body': c.body,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M'),
            'count': post.comments.count()
        }, status=201)
    return JsonResponse({'detail': form.errors.as_json()}, status=400)


@login_required
@require_POST
def api_comment_delete(request, cid):
    c = get_object_or_404(Comment, pk=cid)
    if c.author != request.user and c.post.author != request.user:
        return JsonResponse({'detail': 'FORBIDDEN'}, status=403)
    post = c.post
    c.delete()
    return JsonResponse({'detail': 'DELETED', 'count': post.comments.count()})


@login_required
@require_POST
def api_create(request):
    """AJAX create post, returns rendered card HTML; POST-only & auth-only."""
    content = (request.POST.get("content") or "").strip()
    venue_hint = (request.POST.get("venue_hint") or "").strip()
    if not content:
        return JsonResponse({"detail": "Content is required"}, status=400)

    p = Post.objects.create(author=request.user, content=content, venue_hint=venue_hint)
    html = render_to_string("partials/card.html", {"p": p, "user": request.user})
    return JsonResponse({"html": html}, status=201)

@login_required
def api_post_list(request):
    """Get list of all posts with engagement info."""
    q = (request.GET.get('q') or '').strip()
    qs = Post.objects.select_related('author').annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True),
    ).order_by('-created_at')

    if q:
        qs = qs.filter(Q(content__icontains=q) | Q(venue_hint__icontains=q))

    data = []
    uid = request.user.id
    for p in qs[:50]:
        data.append({
            'id': str(p.id),
            'author': p.author.username,
            'content': p.content,
            'venue_hint': p.venue_hint,
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': p.updated_at.strftime('%Y-%m-%d %H:%M'),
            'like_count': p.like_count,
            'comment_count': p.comment_count,
            'is_liked': p.likes.filter(id=uid).exists(),
            'is_owner': p.author_id == uid,
        })
    return JsonResponse(data, safe=False)


@login_required
def api_post_detail(request, pk):
    """Get a single post with engagement info."""
    post = get_object_or_404(Post, pk=pk)
    post_dict = {
        'id': str(post.id),
        'author': post.author.username,
        'content': post.content,
        'venue_hint': post.venue_hint,
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
        'updated_at': post.updated_at.strftime('%Y-%m-%d %H:%M'),
        'like_count': post.likes.count(),
        'comment_count': post.comments.count(),
        'is_liked': post.likes.filter(id=request.user.id).exists(),
        'is_owner': post.author_id == request.user.id,
    }
    return JsonResponse(post_dict)