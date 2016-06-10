import zk
import urlparse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods as alowed

from .exceptions import ZKError
from .forms import ScanTerminal, SaveTerminal, EditTerminal, UserForm
from .models import Terminal, User

@alowed(['GET'])
@login_required
def index(request):
    return render(request, 'zkcluster/index.html')

@alowed(['GET'])
@login_required
def dashboard(request):
    return render(request, 'zkcluster/dashboard.html')

@alowed(['GET'])
@login_required
def terminal(request):
    terminals = Terminal.objects.all()
    data = {
        'terminals': terminals
    }
    return render(request, 'zkcluster/terminal.html', data)

@alowed(['POST'])
@login_required
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
@login_required
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
                sn = terminal.get_serialnumber()

                # manipulate the POST information
                mutable = request.POST._mutable
                request.POST._mutable = True
                request.POST['serialnumber'] = sn
                request.POST._mutable = mutable

                return terminal_save(request)
            else:
                messages.add_message(request, messages.ERROR, _('can\'t connect to terminal'))
        except Exception, e:
            messages.add_message(request, messages.ERROR, str(e))
        finally:
            if conn:
                terminal.test_voice()
                terminal.enable_device()
                terminal.disconnect()

    data = {
        'form': form
    }

    return render(request, 'zkcluster/terminal_scan.html', data)

@alowed(['GET', 'POST'])
@login_required
def terminal_edit(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    form = EditTerminal(request.POST or None, instance=terminal)
    if request.POST and form.is_valid():
        form.save()
        return redirect('zkcluster:terminal')
    data = {
        'terminal': terminal,
        'form': form
    }
    return render(request, 'zkcluster/terminal_edit.html', data)

@alowed(['POST'])
def terminal_delete(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.delete()
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    return redirect('zkcluster:terminal')

@alowed(['POST'])
def terminal_restart(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.zk_connect()
        terminal.zk_restart()
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    return redirect('zkcluster:terminal')

@alowed(['POST'])
def terminal_poweroff(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.zk_connect()
        terminal.zk_poweroff()
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    return redirect('zkcluster:terminal')

@alowed(['GET', 'POST'])
@login_required
def terminal_action(request, action, terminal_id):
    if action == 'edit':
        return terminal_edit(request, terminal_id)
    elif action == 'restart':
        return terminal_restart(request, terminal_id)
    elif action == 'poweroff':
        return terminal_poweroff(request, terminal_id)
    elif action == 'delete':
        return terminal_delete(request, terminal_id)
    else:
        raise Http404("Action doest not allowed")

@alowed(['GET', 'POST'])
@login_required
def user(request):
    users = User.objects.all()
    data = {
        'users': users
    }
    return render(request, 'zkcluster/user.html', data)

@alowed(['GET', 'POST'])
@login_required
def user_add(request):
    form = UserForm(request.POST or None)
    if request.POST and form.is_valid():
        try:
            form.save()
            return redirect('zkcluster:user')
        except ZKError, e:
            messages.add_message(request, messages.ERROR, str(e))

    data = {
        'form': form
    }
    return render(request, 'zkcluster/user_add.html', data)
