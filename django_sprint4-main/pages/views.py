from django.views.generic import TemplateView
from django.shortcuts import render


class AboutPage(TemplateView):
    """Страница о проекте."""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Страница с правилами."""

    template_name = 'pages/rules.html'


def permission_denied(request, exception=None, reason=''):
    """Обработчик ошибки 403 CSRF."""

    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception=None):
    """Обработчик ошибки 404."""

    return render(request, 'pages/404.html', status=404)


def server_error(request, exception=None):
    """Обработчик ошибки 500."""

    return render(request, 'pages/500.html', status=500)
