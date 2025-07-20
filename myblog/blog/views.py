from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Post

def post_list(request) -> HttpResponse:
    posts = Post.published.all()

    return render(
        request,
        'blog/post/list.html',
        {'posts': posts},
    )

def post_detail(request, id) -> HttpResponse:
    post = get_object_or_404(
        Post,
        id=id,
        status=Post.Status.PUBLISHED
    )
    return render(
        request,
        'blog/post/detail.html',
        {'post': post},
    )
