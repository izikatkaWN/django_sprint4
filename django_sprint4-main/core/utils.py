from django.core.paginator import Paginator
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
    """Добавляет к каждой публикации количество комментариев."""

    return queryset.select_related(
        'author', 'location', 'category'
    ).order_by('-pub_date').annotate(
        comment_count=Count('comments')
    )


def paginate_queryset(queryset, request, per_page=10):
    """Пагинация queryset с извлечением номера страницы из запроса."""
    
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return paginator, page, page_number
