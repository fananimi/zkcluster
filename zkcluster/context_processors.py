from django.http import HttpResponse

from zkcluster.models import Terminal

def terminal(request):
    context_extras = {}
    context_extras['terminals'] = Terminal.objects.all()
    return context_extras
