from django.conf import settings as my_set
from django.core.paginator import Paginator


def mypaginator(request, post_list):
    paginator = Paginator(post_list, my_set.POSTS_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
