from __future__ import unicode_literals

import zk
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext as _
from django.db import models

from .exceptions import ZKError

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

    # @property
    # def terminal(self):
    #     return getattr(self, 'terminal')

    def save(self, *args, **kwargs):
        # connect to terminal
        ip = self.terminal.ip
        port = self.terminal.port
        terminal = zk.ZK(ip, port, 5)
        conn = False
        try:
            conn = terminal.connect()
            if conn:
                setattr(self, 'connection', terminal)
                terminal.disable_device()
            else:
                raise ZKError('can\'t connect to terminal')
        except Exception, e:
            raise ZKError(str(e))

        super(User, self).save(*args, **kwargs)

@receiver(post_save, sender=User)
def on_save_user(sender, **kwargs):
    instance = kwargs['instance']
    conn = instance.connection
    conn.set_user(
        uid=int(instance.id),
        name=str(instance.name),
        privilege=int(instance.privilege),
        password=str(instance.password),
        user_id=str(instance.id)
    )
    conn.test_voice()
    conn.enable_device()
    conn.disconnect()
