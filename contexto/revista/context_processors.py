from django.contrib.sites.models import Site

def site(request):
    SITE = Site.objects.get_current() 
    WTF = "hey!"
    return locals()

