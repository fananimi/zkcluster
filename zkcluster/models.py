from __future__ import unicode_literals

import zk
from zk.exception import ZKError
from django.utils.translation import ugettext_lazy as _
from django.db import models

from .settings import get_terminal_timeout

class Terminal(models.Model):
    name = models.CharField(_('name'), max_length=200)
    serialnumber = models.CharField(_('serialnumber'), max_length=100, unique=True)
    ip = models.CharField(_('ip'), max_length=15, unique=True)
    port = models.IntegerField(_('port'), default=4370)

    class Meta:
        db_table = 'zk_terminal'

    def __init__(self, *arg, **kwargs):
        self.zkconn = None
        super(Terminal, self).__init__(*arg, **kwargs)

    def __unicode__(self):
        return self.name

    def format(self):
        self.zk_connect()
        self.zk_voice()
        self.zk_clear_data()
        self.user_set.clear()

    def zk_connect(self):
        ip = self.ip
        port = self.port
        terminal = zk.ZK(ip, port, get_terminal_timeout())
        conn = terminal.connect()
        if conn:
            terminal.disable_device()
            self.zkconn = terminal
            return self
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

    def zk_get_attendances(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        attendances = self.zkconn.get_attendance()
        return attendances

    def zk_clear_attendances(self):
        if not self.zkconn:
            raise ZKError(_('terminal connection error'))
        self.zkconn.clear_attendance()

class Attendance(models.Model):
    user_id = models.IntegerField(_('user id'))
    terminal = models.ForeignKey(Terminal, related_name='attendances')
    timestamp = models.DateTimeField(_('timestamp'))
    status = models.IntegerField(_('status'))

    class Meta:
        db_table = 'zk_attendance'

    def __unicode__(self):
        return '{}'.format(self.id)

class AbstractUser(models.Model):
    fullname = models.CharField(_('fullname'), max_length=28)

    NAME_FIELD = 'fullname'

    class Meta:
        abstract = True

    def __unicode__(self):
        return getattr(self, 'NAME_FIELD')

class ZKBaseUser(models.Model):
    USER_DEFAULT        = 0
    USER_ADMIN          = 14

    PRIVILEGE_COICES = (
        (USER_DEFAULT, _('User')),
        (USER_ADMIN, _('Administrator'))
    )

    privilege = models.SmallIntegerField(_('privilege'), choices=PRIVILEGE_COICES, default=USER_DEFAULT)
    password = models.CharField(_('password'), max_length=8, blank=True, null=True)
    group_id = models.CharField(_('group id'), max_length=7, blank=True, null=True)

    terminals = models.ManyToManyField(
        Terminal,
        verbose_name=_('terminals'),
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )
    attendances = models.ManyToManyField(
        Attendance,
        verbose_name=_('attendances'),
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True

    def get_privilege_name(self):
        if self.privilege == self.USER_ADMIN:
            return _('Administrator')

        return _('User')

class User(AbstractUser, ZKBaseUser):
    class Meta(AbstractUser.Meta):
        swappable = 'ZK_USER_MODEL'
        db_table = 'zk_user'
