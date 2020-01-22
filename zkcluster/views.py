import zk
from zk.exception import ZKError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods as alowed

from .forms import ScanTerminal, SaveTerminal, EditTerminal, UserForm
from .models import Terminal, User, Attendance

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
def terminal_add(request):
    connected = request.GET.get('connected')
    if connected:
        form = SaveTerminal(request.POST or None, {'validate_name': True})
        if form.is_valid():
            try:
                form.save()
                return redirect('zkcluster:terminal')
            except ZKError, e:
                messages.add_message(request, messages.ERROR, str(e))
    else:
        form = SaveTerminal(request.POST or None)

    data = {
        'form': form
    }
    return render(request, 'zkcluster/terminal_add.html', data)

@alowed(['GET', 'POST'])
@login_required
def terminal_scan(request):
    form = ScanTerminal(request.POST or None)
    if request.POST and form.is_valid():
        ip = form.cleaned_data['ip']
        port = form.cleaned_data['port']
        devicepassword = form.cleaned_data['devicepassword']
        deviceencoding = form.cleaned_data['deviceencoding']
        terminal = Terminal(
            ip=ip,
            port=port,
            devicepassword=devicepassword,
            deviceencoding=deviceencoding
        )
        try:
            terminal.zk_connect()
            sn = terminal.zk_getserialnumber()

            # manipulate the POST information
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['serialnumber'] = sn
            request.POST._mutable = mutable

            terminal.zk_disconnect()
            return terminal_add(request)
        except ZKError, e:
            messages.add_message(request, messages.ERROR, str(e))

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
        try:
            form.save()
        except ZKError, e:
            messages.add_message(request, messages.ERROR, str(e))
        return redirect('zkcluster:terminal')
    data = {
        'terminal': terminal,
        'form': form
    }
    return render(request, 'zkcluster/terminal_edit.html', data)

@alowed(['POST'])
def terminal_format(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.format()
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    return redirect('zkcluster:terminal')

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
        terminal.zk_disconnect()
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))

    return redirect('zkcluster:terminal')

@alowed(['POST'])
def terminal_voice(request, terminal_id):
    terminal = get_object_or_404(Terminal, pk=terminal_id)
    try:
        terminal.zk_connect()
        terminal.zk_voice()
        terminal.zk_disconnect()
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
    elif action == 'voice':
        return terminal_voice(request, terminal_id)
    elif action == 'format':
        return terminal_format(request, terminal_id)
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

@alowed(['GET', 'POST'])
@login_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    form = UserForm(request.POST or None, instance=user)
    if request.POST and form.is_valid():
        try:
            form.save()
            return redirect('zkcluster:user')
        except ZKError, e:
            messages.add_message(request, messages.ERROR, str(e))

    data = {
        'form': form
    }
    return render(request, 'zkcluster/user_edit.html', data)

@alowed(['POST'])
@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    try:
        user.delete()
    except ZKError, e:
        messages.add_message(request, messages.ERROR, str(e))
    return redirect('zkcluster:user')

@alowed(['GET', 'POST'])
@login_required
def user_action(request, action, user_id):
    if action == 'edit':
        return user_edit(request, user_id)
    elif action == 'delete':
        return delete_user(request, user_id)
    else:
        raise Http404("Action doest not allowed")

@alowed(['GET', 'POST'])
@login_required
def attendance(request):
    attendances = Attendance.objects.all().order_by("user_id","timestamp")
    data = {
        'attendances': attendances
    }
    return render(request, 'zkcluster/attendance.html', data)

@alowed(['GET'])
@login_required
def attendance_sync(request):
    terminals = Terminal.objects.all()
    for terminal in terminals:
        try:
            terminal.zk_connect()

            #-- update user
            # print "debug: get user"
            for user in terminal.zk_get_users():
                obj,create = User.objects.update_or_create(
                    user_id=user.user_id,
                    terminal=terminal,
                    defaults={
                    "name":user.name,
                    # "user_id":user.user_id,
                    # "terminal":terminal,
                    "privilege": user.privilege,
                    "password": user.password,
                    "group_id": user.group_id
                })
                # existuser = User.objects.filter(user_id=user.user_id, terminal=terminal)
                # try:
                #     if len(existuser):
                #         # print "edit user"
                #         # existuser.name = user.name,
                #         # existuser.privilege = user.privilege,
                #         # existuser.password = user.password,
                #         # existuser.group_id = user.group_id,
                #         # existuser.user_id = user.user_id,
                #         # existuser.terminal = terminal,
                #         # existuser.update()
                #         pass
                #
                #     else:
                #         # print "add user"
                #         #User.objects.filter().delete()
                #         # print "user.name:" + user.name, user.user_id,  user.uid , user.privilege, user.password , user.card , user.group_id
                #         User.objects.update_or_create(
                #             name = user.name,
                #             privilege = user.privilege,
                #             password = user.password,
                #             group_id = user.group_id,
                #             user_id= user.user_id,
                #             terminal =  terminal,
                #         )
                # except Exception, e:
                #     print "err:", (e)
                #     print "operate user error"
                #     return

            #-- end of user

            #-- get attendance
            print "debug: get attendance"
            for attendance in terminal.zk_get_attendances():
                try:
                    if User.objects.filter(user_id=attendance.user_id).exists():
                        user = User.objects.get(user_id=attendance.user_id)
                        print  "user_id", user.user_id, "user.name", user.name
                        obj,create = Attendance.objects.update_or_create(
                            timestamp=attendance.timestamp,
                            defaults={
                            "user": user,
                            # "timestamp": attendance.timestamp,
                            "status": attendance.status,
                            })

                        # user = User.objects.get(user_id=attendance.user_id)
                        # print  "user_id",user.user_id,"user.name",user.name
                        # existattendance = Attendance.objects.filter(timestamp=attendance.timestamp)
                        # if len(existattendance):
                        #     print "edit attendance"
                        #     # existattendance.user = user,
                        #     # existattendance.timestamp = attendance.timestamp,
                        #     # existattendance.status = attendance.status
                        #     existattendance.update_or_create()
                        # else:
                        #     print "add attendacne"
                        #     # print "user",user,"timestamp",attendance.timestamp,"status",attendance.status
                        #     Attendance.objects.update_or_create(
                        #         user=user,
                        #         timestamp=attendance.timestamp,
                        #         status=attendance.status
                        #     )
                except Exception, e:
                    print "err message:" ,(e)
                    print "operate attendance error"
                    return
#            terminal.zk_clear_attendances()
#            terminal.zk_voice()
            terminal.zk_disconnect()
            #-- end of attendance
        except ZKError, e:
            print "error", ZKError, e
            pass
    return redirect('zkcluster:attendance')
