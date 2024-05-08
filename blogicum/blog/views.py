from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Post, Category
from .forms import PostForm


MAX_POSTS = 5
User = get_user_model()


def get_published_posts(category=None):
    queryset = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
    )

    queryset = queryset.filter(category=category) \
        if category \
        else queryset.filter(category__is_published=True)

    return queryset


class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_published_posts(self.request.GET.get('category'))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('birthday:list')


class UserProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = 10

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()

        # Добавляем информацию о публикациях пользователя
        posts = Post.objects.filter(author=profile_user)
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        # Добавляем информацию, доступную только авторизованному пользователю
        if self.request.user.is_authenticated and self.request.user == profile_user:
            context['can_edit_profile'] = True
            context['can_change_password'] = True

        return context



#
# def index(request):
#     template = 'blog/index.html'
#     post_list = get_published_posts()
#     context = {
#         'post_list': post_list[:MAX_POSTS]
#     }
#     return render(request, template, context)


def post_detail(request, post_id: int):
    template = 'blog/detail.html'
    post = get_object_or_404(
        get_published_posts(),
        pk=post_id
    )
    context = {
        'post': post
    }
    return render(request, template, context)


def category_posts(request, category_slug: str):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_published_posts(category)
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template, context)
