from django.conf import settings

def build_url(*args):
    url = settings.HTTP_OR_HTTPS + settings.MAIN_URL + "/"
    for arg in args:
        url += arg + "/"
    return url
