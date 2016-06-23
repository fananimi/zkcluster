from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed

from zkcluster import get_user_model
from zkcluster.models import Terminal, Attendance

User = get_user_model()

class PauseSignal(object):
    """ Temporarily disconnect a model from a signal """
    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def __enter__(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
            weak=False
        )

    def __exit__(self, type, value, traceback):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
            weak=False
        )

@receiver(pre_save, sender=Terminal)
def pre_save_terminal(sender, **kwargs):
    instance = kwargs['instance']
    instance.zk_connect()
    # generate serialnumber from device
    instance.serialnumber = instance.zk_getserialnumber()
    instance.zk_voice()
    instance.zk_disconnect()

@receiver(pre_save, sender=User)
def pre_save_user(sender, **kwargs):
    instance = kwargs['instance']
    name = getattr(instance, User.NAME_FIELD)
    terminals = []
    try:
        terminals = instance.terminals.all()
    except ValueError, e:
        pass

    for terminal in terminals:
        terminal.zk_connect()
        terminal.zk_setuser(
            uid=instance.id,
            name=name,
            privilege=instance.privilege,
            password=instance.password,
            user_id=instance.id
        )
        terminal.zk_voice()
        terminal.zk_disconnect()

@receiver(pre_delete, sender=User)
def pre_delete_user(sender, **kwargs):
    instance = kwargs['instance']
    terminals = instance.terminals.all()
    for terminal in terminals:
        terminal.zk_connect()
        terminal.zk_delete_user(instance.id)
        terminal.zk_voice()
        terminal.zk_disconnect()

@receiver(m2m_changed, sender=User.terminals.through)
def on_user_add_to_terminal(**kwargs):
    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)
    if action == 'pre_add':
        pass
    if action == 'post_add':
        for terminal in instance.terminals.all():
            terminal.zk_connect()
            name = getattr(instance, User.NAME_FIELD)
            terminal.zk_setuser(
                uid=instance.id,
                name=name,
                privilege=instance.privilege,
                password=instance.password,
                user_id=instance.id
            )

            terminal.zk_voice()
            terminal.zk_disconnect()
    if action == 'pre_remove':
        pass
    if action == 'post_remove':
        pass
