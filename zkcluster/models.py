from __future__ import unicode_literals

import zk
from zk.exception import ZKError
from django.utils.translation import ugettext_lazy as _
from django.db import models

from .settings import get_terminal_timeout

class Terminal(models.Model):
    name = models.CharField(_('name'), max_length=200)
    serialnumber = models.CharField(_('serialnumber'), max_length=100,blank=True ,help_text="device SerialNumber")
    ip = models.CharField(_('ip'), max_length=15, unique=True,help_text="device IP")
    port = models.IntegerField(_('port'), default=4370 ,help_text="device Port")
    devicepassword =models.IntegerField(_('password'),max_length=6,  help_text="device password")
    deviceencoding = models.CharField(_('encoding'), max_length=10,default='gbk',  blank= True, help_text="device content encode:bgk,utf-8...")
    class Meta:
        db_table = 'zk_terminal'

    def __init__(self, *arg, **kwargs):
        self.zkconn = None
        super(Terminal, self).__init__(*arg, **kwargs)

    def __unicode__(self):
        return self.name

    def format(self):
        from signals import PauseSignal
        with PauseSignal(signal=pre_delete, receiver=pre_delete_user, sender=User):
            self.zk_connect()
            self.zk_voice()
            self.zk_clear_data()
            self.users.all().delete()

    def zk_connect(self):
        ip = self.ip
        port = self.port
        devicepassword = self.devicepassword
        deviceencoding = self.deviceencoding
        terminal = zk.ZK(ip, port, get_terminal_timeout(),devicepassword, False,False,False,deviceencoding)
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

    def zk_setuser(self, user):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))

        self.zkconn.set_user(
            uid=int(user.id),
            name=str(user.name),
            privilege=int(user.privilege),
            password=str(user.password),
            user_id=str(user.id)
        )

    def zk_delete_user(self, uid):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.delete_user(uid)

    def zk_get_users(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        zk_get_users = self.zkconn.get_users()
        return  zk_get_users

    def zk_clear_data(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.clear_data()

    def zk_get_attendances(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        attendances = self.zkconn.get_attendance()
        return attendances

    def zk_clear_attendances(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.clear_attendance()

class User(models.Model):
    USER_DEFAULT        = 0
    USER_ADMIN          = 14

    PRIVILEGE_COICES = (
        (USER_DEFAULT, _('User')),
        (USER_ADMIN, _('Administrator'))
    )

    name = models.CharField(_('name'), max_length=28)
    privilege = models.SmallIntegerField(_('privilege'), choices=PRIVILEGE_COICES, default=USER_DEFAULT)
    password = models.CharField(_('password'), max_length=8, blank=True, null=True)
    group_id = models.CharField(_('group id'), max_length=7, blank=True, null=True)
    user_id = models.CharField(_('user_id'), max_length=7, blank=True, null=True)
    #uid = models.CharField(_('uid'), max_length=7, blank=True, null=True)
    terminal = models.ForeignKey(Terminal, blank=True, null=True, on_delete=models.SET_NULL, related_name='users')

    class Meta:
        db_table = 'zk_user'

    def get_privilege_name(self):
        if self.privilege == self.USER_ADMIN:
            return _('Administrator')

        return _('User')

    def __unicode__(self):
        return self.name

class Attendance(models.Model):
    user = models.ForeignKey(User, related_name='attendances')
    timestamp = models.DateTimeField()
    status = models.IntegerField()

    class Meta:
        db_table = 'zk_attendance'

    def __unicode__(self):
        return '{}'.format(self.user.name)

# register signal
from .signals import *
