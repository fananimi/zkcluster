from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Terminal, User


class ScanTerminal(forms.Form):
    ip = forms.CharField(
        label=_('IP Address'),
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': '192.168.200.1',
            'class': 'form-control',
        })
    )
    port = forms.IntegerField(
        label=_('Port'),
        widget=forms.TextInput(attrs={
            'value': 4370,
            'class': 'form-control',
        })
    )

    def clean_ip(self):
        ip = self.cleaned_data.get('ip')
        try:
            if self.instance.ip == ip:
                return ip
        except AttributeError:
            pass

        terminal = Terminal.objects.filter(ip__iexact=ip).first()
        if terminal:
            raise forms.ValidationError(_('IP already exists'))
        return ip

class SaveTerminal(forms.ModelForm, ScanTerminal):
    serialnumber = forms.CharField(
        label=_('Serial Number'),
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': _('Serial number'),
            'class': 'form-control',
            'readonly': True
        })
    )
    name = forms.CharField(
        label=_('Name'),
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': _('Terminal name'),
            'class': 'form-control',
        })
    )

    def __init__(self, *args, **kwargs):
        super(SaveTerminal, self).__init__(*args, **kwargs)
        self.validate_name = False
        if len(args) > 1:
            self.validate_name = args[1].get('validate_name')

        self.fields['ip'].widget = forms.TextInput(attrs={
            'placeholder': _('IP Address'),
            'class': 'form-control',
            'readonly': True
        })
        self.fields['port'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True
        })

    def clean_serialnumber(self):
        serialnumber = self.cleaned_data.get('serialnumber')
        try:
            if self.instance.serialnumber == serialnumber:
                return serialnumber
        except AttributeError:
            pass

        terminal = Terminal.objects.filter(serialnumber__iexact=serialnumber).first()
        if terminal:
            raise forms.ValidationError(_('Serial number already exists'))
        return serialnumber

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.validate_name:
            if not name:
                raise forms.ValidationError(_('This field is required.'))
        return name

    class Meta:
        model = Terminal
        fields = ('ip', 'port', 'serialnumber', 'name')

class EditTerminal(SaveTerminal):
    def __init__(self, *args, **kwargs):
        super(EditTerminal, self).__init__(*args, **kwargs)

        self.fields['ip'].widget = forms.TextInput(attrs={
            'placeholder': _('IP Address'),
            'class': 'form-control'
        })
        self.fields['port'].widget = forms.TextInput(attrs={
            'class': 'form-control'
        })

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'privilege', 'password', 'terminal')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': _('Full name'),
                'class': 'form-control'
            }),
            'privilege': forms.Select(attrs={
                'class': 'form-control'
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': _('Password'),
                'class': 'form-control'
            }),
            'terminal': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and not password.isdigit():
            raise forms.ValidationError(_('Enter a whole number.'))
        return password
