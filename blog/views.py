from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, DetailView

from blog.forms import CommentForm, PostForm, ProfileForm
from blog.models import Category, Comment, Location, Post
from core.constants import PAGINATOR_VALUE
from core.mixins import CommentMixin, IsAuthorMixin, PaginationMixin, PostMixin
from core.utils import annotation_posts_number_comments, filter_publication, paginate_queryset


class RegistrationCreateView(CreateView):
    """Регистрация нового пользователя."""

    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')


class PostListView(PaginationMixin, ListView):
    """Главная страница со списком публикаций."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATOR_VALUE

    def get_queryset(self):
        return annotation_posts_number_comments(
            filter_publication(super().get_queryset())
        )
    
    def paginate_queryset(self, queryset, page_size):
        """Переопределяем метод пагинации для использования вынесенной функции."""

        return super().paginate_queryset(queryset, page_size)


class PostDetailListView(DetailView):
    """Страница отдельной публикации с комментариями."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        """Возвращает пост или вызывает 404, если пост недоступен."""

        post = super().get_object(queryset)
        if post.author != self.request.user and not post.is_published:
            raise Http404('Публикация не найдена')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class CategoryPostsListView(PaginationMixin, ListView):
    """Страница со списком публикаций в категории."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATOR_VALUE

    def get_category(self):
        """Возвращает категорию или 404, если категория не опубликована."""

        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return annotation_posts_number_comments(
            filter_publication(self.get_category().posts.all())
        )
    
    def paginate_queryset(self, queryset, page_size):
        """Переопределяем метод пагинации для использования вынесенной функции."""

        return super().paginate_queryset(queryset, page_size)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class GetProfileListView(PaginationMixin, ListView):
    """Страница профиля пользователя."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATOR_VALUE

    def get_author(self):
        """Возвращает пользователя или 404."""

        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        user = self.get_author()
        queryset = annotation_posts_number_comments(user.posts.all())
        if user != self.request.user:
            queryset = filter_publication(queryset)
        return queryset
    
    def paginate_queryset(self, queryset, page_size):
        """Переопределяем метод пагинации для использования вынесенной функции."""

        return super().paginate_queryset(queryset, page_size)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        """Всегда возвращаем текущего пользователя."""

        return self.request.user
    
    def get_success_url(self):
        """После редактирования перенаправляем на страницу профиля."""

        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание новой публикации."""

    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать публикацию'
        return context


class PostUpdateView(PostMixin, UpdateView):
    """Редактирование публикации."""
    
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать публикацию'
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление публикации."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')
    
    def dispatch(self, request, *args, **kwargs):
        """Проверяем, что пользователь - автор поста."""

        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post.id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удалить публикацию'
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""
    
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование комментария."""
    
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    
    def dispatch(self, request, *args, **kwargs):
        """Проверяем, что пользователь - автор комментария."""

        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=comment.post.id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'post_id': comment.post.id})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление комментария."""
    
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    success_url = reverse_lazy('blog:index') 
    
    def dispatch(self, request, *args, **kwargs):
        """Проверяем, что пользователь - автор комментария."""

        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=comment.post.id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        """После удаления перенаправляем на страницу поста."""

        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'post_id': comment.post.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удалить комментарий'
        if 'form' in context:
            context['form'] = None
        return context
    
    def post(self, request, *args, **kwargs):
        """Обрабатываем POST-запрос на удаление."""

        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)
