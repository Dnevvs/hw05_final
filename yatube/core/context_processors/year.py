from django.utils import timezone


def year(request):
    result = timezone.now().year
    return {'year': result}
