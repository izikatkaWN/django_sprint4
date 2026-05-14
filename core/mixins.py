from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from blog.forms import CommentForm, PostForm
from blog.models import Comment, Post


class IsAuthorMixin(UserPassesTestMixin):
    """Проверка, что пользователь является автором объекта."""
    
    def test_func(self):
        return self.get_object().author == self.request.user


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
            kwargs={'username_slug': self.request.user.username}
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
    