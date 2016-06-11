from __future__ import unicode_literals

import zk
from zk.exception import ZKError
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _
from django.db import models

from .settings import get_terminal_timeout

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

    def format(self):
        '''
        not implemented yet
        '''
        # self.zk_connect()
        # self.zk_voice()
        # self.zk_clear_data()
        # self.users.all().delete()

    def zk_connect(self):
        ip = self.ip
        port = self.port
        terminal = zk.ZK(ip, port, get_terminal_timeout())
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

    def zk_getserialnumber(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        sn = self.zkconn.get_serialnumber()
        return sn

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

    def zk_delete_user(self, uid):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.delete_user(uid)

    def zk_clear_data(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.clear_data()

# make sure the terminal is available
@receiver(pre_save, sender=Terminal)
def pre_save_terminal(sender, **kwargs):
    instance = kwargs['instance']
    instance.zk_connect()
    instance.serialnumber = instance.zk_getserialnumber()
    instance.zk_voice()
    instance.zk_disconnect()

# generate uid counter used by user
@receiver(post_save, sender=Terminal)
def on_save_terminal(sender, **kwargs):
    instance = kwargs['instance']
    counter = UIDCounter.objects.filter(terminal=instance).first()
    if not counter:
        UIDCounter.objects.create(next_uid=1, terminal=instance)

class DeletedUID(models.Model):
    uid = models.IntegerField()
    terminal = models.ForeignKey(Terminal, related_name='deleted_uids')

    def __unicode__(self):
        return '{}'.format(self.uid)

class UIDCounter(models.Model):
    next_uid = models.IntegerField()
    terminal = models.OneToOneField(Terminal, related_name='counter')

    def __unicode__(self):
        return '{}'.format(self.next_uid)

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
    terminal = models.ForeignKey(Terminal, related_name='users')

    def get_privilege_name(self):
        if self.privilege == self.USER_ADMIN:
            return _('Administrator')

        return _('User')

    def __unicode__(self):
        return self.name

@receiver(pre_save, sender=User)
def pre_save_user(sender, **kwargs):
    instance = kwargs['instance']
    terminal = instance.terminal

    terminal.zk_connect()

    if instance.uid:
        terminal.zk_setuser(
            instance.uid,
            instance.name,
            instance.privilege,
            instance.password,
            instance.uid
        )
        terminal.zk_voice()
        terminal.zk_disconnect()
    else:
        available_uid = DeletedUID.objects.filter(terminal=terminal).first()
        if available_uid:
            instance.uid = available_uid.uid
        else:
            instance.uid = terminal.counter.next_uid

        terminal.zk_setuser(
            instance.uid,
            instance.name,
            instance.privilege,
            instance.password,
            instance.uid
        )
        terminal.zk_voice()
        terminal.zk_disconnect()

        if available_uid:
            available_uid.delete()
        else:
            terminal.counter.next_uid += 1
            terminal.counter.save()

@receiver(pre_delete, sender=User)
def pre_delete_user(sender, **kwargs):
    instance = kwargs['instance']
    DeletedUID.objects.create(
        uid=instance.uid,
        terminal=instance.terminal
    )
