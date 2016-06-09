from django.shortcuts import render

from .models import Terminal

def index(request):
    return render(request, 'zkcluster/index.html')

def dashboard(request):
    return render(request, 'zkcluster/dashboard.html')

def terminal(request):
    terminals = Terminal.objects.all()
    data = {
        'terminals': terminals
    }
    return render(request, 'zkcluster/terminal.html', data)