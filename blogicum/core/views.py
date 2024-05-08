from django.shortcuts import render


def page_not_found(request, *args, template_name='pages/404.html', **kwargs):
    return render(request, template_name, status=404)


def server_error(request, *args, template_name='pages/500.html', **kwargs):
    return render(request, template_name, status=500)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
