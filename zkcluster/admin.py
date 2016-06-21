from zk.exception import ZKError

from django import forms
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _

from zkcluster import get_user_model
from zkcluster.models import Terminal, Attendance

User = get_user_model()

class TerminalAdminForm(forms.ModelForm):
    class Meta:
        model = Terminal
        fields = ('name', 'ip', 'port')

    def clean_ip(self):
        ip = self.cleaned_data.get('ip')
        if hasattr(self.instance, 'ip'):
            if self.instance.ip == ip:
                return ip

        terminal = Terminal.objects.filter(ip__iexact=ip).first()
        if terminal:
            raise forms.ValidationError(_('IP already exists'))

        return ip

    def clean(self):
        cleaned_data = self.cleaned_data

        ip = cleaned_data.get('ip')
        port = cleaned_data.get('port')
        if ip and port:
            conn = None
            terminal = Terminal(ip=ip, port=port)
            try:
                conn = terminal.zk_connect()
            except ZKError, e:
                data = {'ip': ip, 'port': port}
                err_msg = _('can\'t connect to udp://%(ip)s:%(port)s' % data)
                raise forms.ValidationError(err_msg)
            finally:
                if conn:
                    conn.zk_disconnect()

        return cleaned_data

class TerminalAdmin(admin.ModelAdmin):
    form = TerminalAdminForm
    list_display = ('name', 'serialnumber', 'ip', 'port')

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('attendances',)

    def clean(self):
        cleaned_data = self.cleaned_data
        terminals = cleaned_data.get('terminals')

        for terminal in terminals:
            conn = False
            try:
                conn = terminal.zk_connect()
            except ZKError, e:
                data = {
                    'ip': terminal.ip,
                    'port': terminal.port
                }
                err_msg = _('can\'t connect to udp://%(ip)s:%(port)s' % data)
                raise forms.ValidationError(err_msg)
            finally:
                if conn:
                    conn.zk_disconnect()

        return cleaned_data

class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ('name', 'privilege', 'password', 'group_id')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'terminal', 'timestamp', 'status')

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return (request.method in ['GET', 'HEAD'] and super(AttendanceAdmin, self).has_change_permission(request, obj))

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        css = {'all': ('zkcluster/css/hide_save_button.css', )}

admin.site.register(Terminal, TerminalAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Attendance, AttendanceAdmin)
