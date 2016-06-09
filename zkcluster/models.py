from __future__ import unicode_literals

from django.db import models

class Terminal(models.Model):
    name = models.CharField(max_length=200)
    serialnumber = models.CharField(max_length=100, unique=True)
    ip = models.CharField(max_length=15, unique=True)
    port = models.IntegerField(default=4370)

    def __unicode__(self):
        return self.name
