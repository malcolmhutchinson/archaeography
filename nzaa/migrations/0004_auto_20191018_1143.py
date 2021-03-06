# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-10-17 22:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nzaa', '0003_auto_20190308_0941'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('stored_directory', models.CharField(max_length=255)),
                ('orig_disp', models.CharField(choices=[('original', 'original'), ('display', 'display')], default='display', max_length=16)),
                ('fileformat', models.CharField(max_length=8)),
                ('downloaded', models.DateTimeField(default='2019-01-01 00:00:00')),
            ],
            options={
                'ordering': ['filename'],
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('doctype', models.CharField(blank=True, max_length=255, null=True)),
                ('author', models.CharField(blank=True, max_length=1024, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('description', models.TextField()),
                ('fileformat', models.CharField(max_length=8)),
                ('downloaded', models.DateTimeField(default='2019-01-01 00:00:00')),
                ('update', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nzaa.Update')),
            ],
            options={
                'ordering': ['date', 'filename'],
            },
        ),
        migrations.AddField(
            model_name='docfile',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='nzaa.Document'),
        ),
    ]
