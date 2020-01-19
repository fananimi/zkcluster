# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zkcluster', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.CharField(max_length=7, null=True, verbose_name='user_id', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='terminal',
            name='deviceencoding',
            field=models.CharField(default='gbk', help_text='device content encode:bgk,utf-8...', max_length=10, verbose_name='encoding', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='terminal',
            name='devicepassword',
            field=models.IntegerField(default=111111, help_text='device password', max_length=6, verbose_name='password'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='terminal',
            name='ip',
            field=models.CharField(help_text='device IP', unique=True, max_length=15, verbose_name='ip'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='terminal',
            name='port',
            field=models.IntegerField(default=4370, help_text='device Port', verbose_name='port'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='terminal',
            name='serialnumber',
            field=models.CharField(help_text='device SerialNumber', max_length=100, verbose_name='serialnumber', blank=True),
            preserve_default=True,
        ),

    ]
