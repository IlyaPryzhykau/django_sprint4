from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import Http404
from django.shortcuts import (get_object_or_404,
                              redirect)
from django.urls import (reverse,
                         reverse_lazy)
from django.utils import timezone
from django.views.generic import (CreateView,
                                  DeleteView,
                                  DetailView,
                                  ListView,
                                  UpdateView)

from .forms import (PostForm,
                    CommentForm)
from .models import (Category,
                     Comment,
                     Post)


SORT_ORDER = '-pub_date'

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    raise_exception = True  # Генерирует 403 ошибку, если тест не прошел

    def test_func(self):
        return self.get_object().author == self.request.user

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


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
        queryset = (get_published_posts()
                    .annotate(comment_count=Count('comments'))
                    .order_by(SORT_ORDER))
        return queryset

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


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


class UserProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if user == self.request.user:
            queryset = (get_published_posts(user=user)
                        .annotate(comment_count=Count('comments'))
                        .order_by(SORT_ORDER))
        else:
            queryset = (get_published_posts()
                        .filter(author=user)
                        .annotate(comment_count=Count('comments'))
                        .order_by(SORT_ORDER))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author_user = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = author_user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'email', 'username')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostEditView(OnlyAuthorMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        if not (post.is_published and post.category.is_published
                and post.pub_date <= timezone.now()):
            if post.author != self.request.user:
                raise Http404("Страница не найдена")

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('created_at')
        context['form'] = CommentForm()
        return context


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


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
        return (get_published_posts(category=self.category)
                .annotate(comment_count=Count('comments'))
                .order_by(SORT_ORDER))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentEditView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.id})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.id})
