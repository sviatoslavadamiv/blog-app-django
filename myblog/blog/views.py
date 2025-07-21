from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail

from .forms import EmailPostForm, CommentForm
from .models import Post

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

# def post_list(request) -> HttpResponse:
#     post_list = Post.published.all()
#
#     # Pagination with 3 posts per page
#     paginator = Paginator(post_list, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except PageNotAnInteger:
#         # If page_number is not an integer get the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page_number is out of range get last page of results
#         posts = paginator.page(paginator.num_pages)
#
#     return render(
#         request,
#         'blog/post/list.html',
#         {'posts': posts},
#     )

class PostDetailView(DetailView):
    queryset = Post.published.all()
    template_name = 'blog/post/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        return get_object_or_404(
            queryset,
            slug=self.kwargs.get('post'),
            publish__year=self.kwargs.get('year'),
            publish__month=self.kwargs.get('month'),
            publish__day=self.kwargs.get('day'),
        )

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        # List of active comments for this post
        comments = self.get_object().comments.filter(active=True)
        # Form for user to comment
        form = CommentForm()
        context["comments"] = comments
        context["form"] = form
        return context


# def post_detail(request, year, month, day, post) -> HttpResponse:
#     post = get_object_or_404(
#         Post,
#         status=Post.Status.PUBLISHED,
#         slug=post,
#         publish__year=year,
#         publish__month=month,
#         publish__day=day,
#     )
#     return render(
#         request,
#         'blog/post/detail.html',
#         {'post': post},
#     )


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False

    if request.method == 'POST':
        # From was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']],
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent,
        }
    )

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment,
        }
    )

