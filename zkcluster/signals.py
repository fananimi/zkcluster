from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save, post_save, pre_delete

from .models import Terminal, User

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
    instance.serialnumber = instance.zk_getserialnumber()
    instance.zk_voice()
    instance.zk_disconnect()

# @receiver(pre_save, sender=User)
# def pre_save_user(sender, **kwargs):
#     instance = kwargs['instance']
#     terminal = instance.terminal
#     terminal.zk_connect()

# @receiver(post_save, sender=User)
# def post_save_user(sender, **kwargs):
#     instance = kwargs['instance']
#     terminal = instance.terminal

#     terminal.zk_setuser(instance)
#     terminal.zk_voice()
#     terminal.zk_disconnect()

@receiver(pre_delete, sender=User)
def pre_delete_user(sender, **kwargs):
    instance = kwargs['instance']

    if instance.terminal:
        terminal = instance.terminal
        terminal.zk_connect()
        terminal.zk_delete_user(instance.id)
        terminal.zk_disconnect()
