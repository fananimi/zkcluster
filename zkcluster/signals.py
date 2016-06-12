from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save, pre_save, pre_delete

from .models import Terminal, User, DeletedUID, UIDCounter

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

    if instance.terminal:
        terminal = instance.terminal
        terminal.zk_connect()
        terminal.zk_delete_user(instance.uid)
        terminal.zk_disconnect()

        DeletedUID.objects.create(
            uid=instance.uid,
            terminal=instance.terminal
        )
