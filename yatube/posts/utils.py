from django.core.paginator import Paginator

from yatube.settings import COUNT_POST_VIEWS


def get_paginator(queryset, request):
    paginator = Paginator(queryset, COUNT_POST_VIEWS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
