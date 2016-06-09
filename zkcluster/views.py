from django.shortcuts import render, redirect

from .models import Terminal
from .forms import ScanTerminal, AddTerminal

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

def terminal_scan(request):
    form = ScanTerminal(request.POST or None)
    if request.POST and form.is_valid():
        return redirect('zkcluster:terminal_add')
    data = {
        'form': form
    }
    return render(request, 'zkcluster/terminal_scan.html', data)


def terminal_add(request):
    form = AddTerminal(request.POST or None)
    data = {
        'form': form
    }
    return render(request, 'zkcluster/terminal_add.html', data)
