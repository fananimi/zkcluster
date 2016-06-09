import zk
import urlparse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods as alowed

from .models import Terminal
from .forms import ScanTerminal, SaveTerminal

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

@alowed(['POST'])
def terminal_save(request):
    connected = request.GET.get('connected')
    if connected:
        form = SaveTerminal(request.POST or None, {'validate_name': True})
        if form.is_valid():
            form.save()
            return redirect('zkcluster:terminal')
    else:
        form = SaveTerminal(request.POST or None)

    data = {
        'form': form
    }
    return render(request, 'zkcluster/terminal_save.html', data)

@alowed(['GET', 'POST'])
def terminal_add(request):
    form = ScanTerminal(request.POST or None)
    if request.POST and form.is_valid():
        ip = form.cleaned_data['ip']
        port = form.cleaned_data['port']

        # connect to terminal
        terminal = zk.ZK(ip, port, 5)
        conn = False
        try:
            conn = terminal.connect()
            if conn:
                terminal.disable_device()
                terminal.test_voice()
                sn = terminal.get_serialnumber()

                # manipulate the POST information
                mutable = request.POST._mutable
                request.POST._mutable = True
                request.POST['serialnumber'] = sn
                request.POST._mutable = mutable

                terminal.enable_device()
                return terminal_save(request)
            else:
                messages.add_message(request, messages.ERROR, 'can\'t connect to terminal')
        except Exception, e:
            messages.add_message(request, messages.ERROR, str(e))
        finally:
            if conn:
                terminal.disconnect()

    data = {
        'form': form
    }

    return render(request, 'zkcluster/terminal_scan.html', data)
