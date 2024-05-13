from django.views.generic import TemplateView
from django.shortcuts import render


FORBIDDEN = 403
INTERNAL_SERVER_ERROR = 500
NOT_FOUND = 404


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class RulesPageView(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, *args, template_name='pages/404.html', **kwargs):
    return render(request, template_name, status=NOT_FOUND)


def server_error(request, *args, template_name='pages/500.html', **kwargs):
    return render(request, template_name, status=INTERNAL_SERVER_ERROR)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=FORBIDDEN)


def permission_denied(request, exception):
    return render(request, 'pages/403.html', status=FORBIDDEN)
