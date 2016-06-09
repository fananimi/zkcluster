from django import forms
from django.utils.translation import ugettext as _


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

class AddTerminal(ScanTerminal):
    serialnumber = forms.CharField(
        label=_('Serial Number'),
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': _('Serial number'),
            'class': 'form-control',
        })
    )
    name = forms.CharField(
        label=_('Name'),
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': _('Terminal name'),
            'class': 'form-control',
        })
    )
