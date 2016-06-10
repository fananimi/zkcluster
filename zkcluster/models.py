from __future__ import unicode_literals

import zk
from zk.exception import ZKError
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _
from django.db import models

class Terminal(models.Model):
    name = models.CharField(_('name'), max_length=200)
    serialnumber = models.CharField(_('serialnumber'), max_length=100, unique=True)
    ip = models.CharField(_('ip'), max_length=15, unique=True)
    port = models.IntegerField(_('port'), default=4370)

    def __init__(self, *arg, **kwargs):
        self.zkconn = None
        super(Terminal, self).__init__(*arg, **kwargs)

    def __unicode__(self):
        return self.name

    def zk_connect(self):
        ip = self.ip
        port = self.port
        terminal = zk.ZK(ip, port, 5)
        conn = terminal.connect()
        if conn:
            terminal.disable_device()
            self.zkconn = terminal
        else:
            raise ZKError(_('can\'t connect to terminal'))

    def zk_disconnect(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.enable_device()
        self.zkconn.disconnect()

    def zk_restart(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.restart()

    def zk_poweroff(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.poweroff()

    def zk_voice(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.test_voice()

    def zk_setuser(self, uid, name, privilege, password, user_id):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))

        self.zkconn.set_user(
            uid=int(uid),
            name=str(name),
            privilege=int(privilege),
            password=str(password),
            user_id=str(user_id)
        )

    def zk_clear_data(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.clear_data()

@receiver(pre_delete, sender=Terminal)
def pre_delete_terminal(sender, **kwargs):
    instance = kwargs['instance']
    instance.zk_connect()

@receiver(post_delete, sender=Terminal)
def on_delete_terminal(sender, **kwargs):
    instance = kwargs['instance']
    instance.zk_voice()
    instance.zk_clear_data()

class User(models.Model):
    USER_DEFAULT        = 0
    USER_ADMIN          = 14

    PRIVILEGE_COICES = (
        (USER_DEFAULT, _('User')),
        (USER_ADMIN, _('Administrator'))
    )

    uid = models.IntegerField(_('uid'))
    name = models.CharField(_('name'), max_length=28)
    privilege = models.SmallIntegerField(_('privilege'), choices=PRIVILEGE_COICES, default=USER_DEFAULT)
    password = models.CharField(_('password'), max_length=8, blank=True, null=True)
    group_id = models.CharField(_('group id'), max_length=7, blank=True, null=True)
    terminal = models.ForeignKey(Terminal, related_name='zkuser')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            latest_user = User.objects.filter(terminal=self.terminal).latest('id')
            uid = latest_user.uid + 1
        except User.DoesNotExist:
            uid = 1

        self.uid = uid
        self.terminal.zk_connect()
        super(User, self).save(*args, **kwargs)

@receiver(post_save, sender=User)
def on_save_user(sender, **kwargs):
    instance = kwargs['instance']
    instance.terminal.zk_setuser(
        instance.id,
        instance.name,
        instance.privilege,
        instance.password,
        instance.uid
    )
    instance.terminal.zk_voice()
    instance.terminal.zk_disconnect()
