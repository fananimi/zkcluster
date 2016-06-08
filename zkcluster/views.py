from django.shortcuts import render

def index(request):
    return render(request, 'zkcluster/index.html')

def dashboard(request):
    return render(request, 'zkcluster/dashboard.html')

def terminal(request):
    return render(request, 'zkcluster/terminal.html')