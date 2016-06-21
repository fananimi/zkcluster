from __future__ import unicode_literals

from django.apps import AppConfig
from importlib import import_module


class ZkclusterConfig(AppConfig):
    name = 'zkcluster'
    verbose_name = 'zkcluster'

    def ready(self):
        import_module('zkcluster.signals')
