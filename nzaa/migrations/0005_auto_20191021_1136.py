# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-10-20 22:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nzaa', '0004_auto_20191018_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='docfile',
            name='ordinal',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='document',
            name='quality',
            field=models.CharField(choices=[('acceptable', 'acceptable'), ('poor', 'poor'), ('unknown', 'unknown'), ('unreadable', 'unreadable')], default='unknown', max_length=255),
        ),
        migrations.AddField(
            model_name='document',
            name='uri',
            field=models.CharField(blank=True, editable=False, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='doctype',
            field=models.CharField(blank=True, choices=[('Aerial photo', 'Aerial photo'), ('Drawing', 'Drawing'), ('Figure', 'Figure'), ('Map', 'Map'), ('Note', 'Note'), ('Photo reference form', 'Photo reference form'), ('Photograph(s)', 'Photograph(s)'), ('Report', 'Report'), ('Site description form', 'Site description form'), ('Site record form', 'Site record form'), ('Site reference form', 'Site reference form'), ('Site report form', 'Site report form'), ('Site update form', 'Site update form')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='downloaded',
            field=models.DateTimeField(default='2019-01-01 00:00:00+12', editable=False),
        ),
        migrations.AlterField(
            model_name='document',
            name='fileformat',
            field=models.CharField(editable=False, max_length=8),
        ),
    ]
