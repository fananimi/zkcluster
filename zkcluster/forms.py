from django import forms
from django.utils.translation import ugettext as _

from .models import Terminal


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
        terminal = Terminal.objects.filter(serialnumber__iexact=serialnumber).first()
        if terminal:
            raise forms.ValidationError(_('Serial number already exists'))
        return serialnumber

    class Meta:
        model = Terminal
        fields = ('ip', 'port', 'serialnumber', 'name')
