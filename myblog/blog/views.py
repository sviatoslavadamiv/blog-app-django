from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity

from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post
from taggit.models import Tag

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        queryset = Post.published.all()
        self.tag = None
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[self.tag])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


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

        # List of similar posts
        post_tags_ids = self.get_object().tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=self.get_object().id)
        similar_posts = similar_posts.annotate(
            same_tags=Count('tags')
        ).order_by('-same_tags', '-publish')[:4]

        context["comments"] = comments
        context["form"] = form
        context["similar_posts"] = similar_posts
        return context


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

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # Search vector
            # search_vector = SearchVector('title', 'body')
            # search_query = SearchQuery(query)
            # results = (
            #     Post.published.annotate(
            #         search=search_vector,
            #         rank=SearchRank(search_vector, search_query),
            #     )
            #     .filter(search=search_query)
            #     .order_by('-rank')
            # )

            # Search vector with weights
            # search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            # search_query = SearchQuery(query)
            # results = (
            #     Post.published.annotate(
            #         search=search_vector,
            #         rank=SearchRank(search_vector, search_query)
            #     )
            #     .filter(rank__gte=0.3)
            #     .order_by('-rank')
            # )

            # Search with trigram similarity
            results = (
                Post.published.annotate(
                    similarity=TrigramSimilarity('title', query),
                )
                .filter(similarity__gt=0.05)
                .order_by('-similarity')
            )

    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'results': results,
        }
    )

