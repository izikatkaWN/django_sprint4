from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from blog.forms import CommentForm, PostForm
from blog.models import Comment, Post
from core.utils import paginate_queryset


class IsAuthorMixin(UserPassesTestMixin):
    """Проверка, что пользователь является автором объекта."""
    
    def test_func(self):
        return self.get_object().author == self.request.user


class PaginationMixin:
    """Миксин для пагинации с вынесенной логикой."""
    
    paginate_by = 10
    
    def paginate_queryset(self, queryset, page_size):
        """Пагинация queryset с использованием вынесенной функции."""

        paginator, page, page_number = paginate_queryset(
            queryset, self.request, page_size
        )
        return (paginator, page, page.object_list, page.has_other_pages())


class PostMixin(IsAuthorMixin, LoginRequiredMixin):
    """Миксин для работы с постами."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs[self.pk_url_kwarg]
        )

    def get_success_url(self):
        """По умолчанию перенаправляем на профиль."""

        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать публикацию'
        return context


class CommentMixin(LoginRequiredMixin):
    """Миксин для работы с комментариями."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'delete_comment' in self.request.path:
            context['form'] = None
        return context
