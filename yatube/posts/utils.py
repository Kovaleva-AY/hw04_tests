from django.core.paginator import Paginator


def get_page_context(request, queryset, pages: int):
    paginator = Paginator(queryset, pages)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
