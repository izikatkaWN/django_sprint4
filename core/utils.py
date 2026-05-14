"""Утилиты для работы с QuerySet в Blogicum."""

from django.db.models import Count
from django.utils.timezone import now


def filter_publication(queryset):
    """Фильтрует QuerySet публикаций для публичного отображения."""
    
    return queryset.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    )


def annotation_posts_number_comments(queryset):
    """Добавляет к каждой публикации количество комментариев. """

    return queryset.select_related(
        'author', 'location', 'category'
    ).order_by('-pub_date').annotate(
        comment_count=Count('comments')
    )
