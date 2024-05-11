from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.generic import (
    DetailView, ListView, CreateView, UpdateView, DeleteView)
from django.core.paginator import Paginator
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin)
from django.urls import reverse, reverse_lazy
from django.db.models import Count
from django.http import Http404

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm


MAX_POSTS = 5
User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    raise_exception = True  # Генерирует 403 ошибку, если тест не прошел

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


def get_published_posts(category=None, user=None):
    now = timezone.now()
    queryset = Post.objects.all()

    if category:
        queryset = queryset.filter(category=category)

    if user:
        queryset = queryset.filter(author=user)
    else:
        queryset = queryset.filter(
            is_published=True, pub_date__lte=now, category__is_published=True)

    return queryset


class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = get_published_posts()
        queryset = queryset.annotate(comment_count=Count('comments'))
        queryset = queryset.order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class UserProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = 10

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        author_user = self.get_object()
        user = self.request.user

        if author_user == user:
            posts = get_published_posts(user=user).order_by('-pub_date')
        else:
            posts = (get_published_posts().filter(
                author=author_user).order_by('-pub_date'))

        posts_with_comment_count = posts.annotate(
            comment_count=Count('comments'))

        paginator = Paginator(posts_with_comment_count, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'email', 'username']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class EditPostView(OnlyAuthorMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        if not post.is_published or not post.category.is_published:
            if post.author != self.request.user:
                raise Http404("Страница не найдена")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        comments = post.comments.all().order_by('created_at')
        context['comments'] = comments
        context['form'] = CommentForm()
        return context


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        queryset = get_published_posts(
            category=self.category).order_by('-pub_date')
        queryset = queryset.annotate(comment_count=Count('comments'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment_id = self.kwargs['comment_id']
        comment = get_object_or_404(Comment, pk=comment_id)
        return comment

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != self.request.user:
            return redirect('blog:post_detail', post_id=comment.post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        comment = self.object
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': comment.post.pk}
        )


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_id = self.object.post.id
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': post_id}
        )
