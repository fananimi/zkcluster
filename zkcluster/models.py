from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from django.db import models

class Terminal(models.Model):
    name = models.CharField(max_length=200)
    serialnumber = models.CharField(max_length=100, unique=True)
    ip = models.CharField(max_length=15, unique=True)
    port = models.IntegerField(default=4370)

    def __unicode__(self):
        return self.name

class User(models.Model):
    USER_DEFAULT        = 0
    USER_ADMIN          = 14

    PRIVILEGE_COICES = (
        (USER_DEFAULT, _('User')),
        (USER_ADMIN, _('Administrator'))
    )

    name = models.CharField(max_length=28)
    privilege = models.SmallIntegerField(choices=PRIVILEGE_COICES, default=USER_DEFAULT)
    password = models.CharField(max_length=8, blank=True, null=True)
    group_id = models.CharField(max_length=7, blank=True, null=True)
    terminal = models.ForeignKey(Terminal, related_name='zkuser')

    def __unicode__(self):
        return self.name
