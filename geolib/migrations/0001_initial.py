# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-31 01:32
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AerialFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('uri', models.CharField(max_length=1024)),
                ('file_format', models.CharField(max_length=255)),
                ('received', models.DateField()),
                ('received_fname', models.CharField(max_length=255)),
                ('uploaded', models.DateField(blank=True, null=True)),
                ('uploaded_by', models.CharField(blank=True, max_length=255, null=True)),
                ('provenance', models.TextField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('filetype', models.CharField(choices=[('crop', 'crop'), ('points', 'points'), ('ref_high', 'ref_high'), ('ref_low', 'ref_low'), ('source_high', 'source_high'), ('source_low', 'source_low')], max_length=255)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=2193)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AerialFrame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=16)),
                ('ordinal', models.IntegerField(blank=True, null=True)),
                ('date_flown', models.DateField(blank=True, null=True)),
                ('time_flown', models.TimeField(blank=True, null=True)),
                ('alt_ft', models.PositiveIntegerField(blank=True, null=True)),
                ('alt_m', models.PositiveIntegerField(blank=True, null=True)),
                ('focal_length', models.CharField(blank=True, max_length=16, null=True)),
                ('aperture', models.CharField(blank=True, max_length=32, null=True)),
                ('status', models.CharField(blank=True, choices=[(None, '-'), ('for reference', 'for reference'), ('polynomial', 'polynomial'), ('thin plate spline', 'thin plate  spline')], default=None, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('georef_notes', models.TextField(blank=True, null=True)),
                ('source_url', models.CharField(blank=True, max_length=2014, null=True)),
                ('coverage', models.CharField(blank=True, max_length=255, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('rights', models.CharField(blank=True, max_length=255, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=2193)),
            ],
            options={
                'ordering': ('run', 'ordinal'),
            },
        ),
        migrations.CreateModel(
            name='AerialRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=16)),
                ('ordinal', models.IntegerField(blank=True, null=True)),
                ('direction', models.CharField(blank=True, max_length=255, null=True)),
                ('rights', models.CharField(blank=True, max_length=255, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=2193)),
            ],
            options={
                'ordering': ('survey', 'ordinal'),
            },
        ),
        migrations.CreateModel(
            name='AerialSurvey',
            fields=[
                ('identifier', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('ordinal', models.IntegerField(editable=False)),
                ('name', models.CharField(blank=True, max_length=1024, null=True)),
                ('year_first', models.PositiveIntegerField(blank=True, null=True)),
                ('year_last', models.PositiveIntegerField(blank=True, null=True)),
                ('film_type', models.CharField(blank=True, choices=[('B&W', 'B&W'), ('colour', 'colour'), ('infrared', 'infrared')], max_length=255, null=True)),
                ('rights', models.CharField(blank=True, max_length=255, null=True)),
                ('comments', models.CharField(blank=True, max_length=255, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=2193)),
            ],
            options={
                'ordering': ('ordinal',),
            },
        ),
        migrations.CreateModel(
            name='Cadastre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appellation', models.TextField(blank=True, null=True)),
                ('affected_surveys', models.TextField(blank=True, null=True)),
                ('parcel_intent', models.TextField(blank=True, null=True)),
                ('topology_type', models.TextField(blank=True, null=True)),
                ('statutory_actions', models.TextField(blank=True, null=True)),
                ('land_district', models.TextField(blank=True, null=True)),
                ('titles', models.TextField(blank=True, null=True)),
                ('survey_area', models.FloatField(blank=True, null=True)),
                ('calc_area', models.FloatField(blank=True, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='LidarSet',
            fields=[
                ('identifier', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('year_captured', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('imagelayer_uri', models.CharField(blank=True, max_length=1024, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='LidarTile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('local_fname', models.CharField(blank=True, max_length=255, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2193)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiles', to='geolib.LidarSet')),
            ],
            options={
                'ordering': ('identifier',),
            },
        ),
        migrations.CreateModel(
            name='NZMSgrid',
            fields=[
                ('identifier', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('sheet_name', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=2193)),
                ('record_region', models.CharField(blank=True, max_length=255, null=True)),
                ('nzms_xmax', models.IntegerField()),
                ('nzms_xmin', models.IntegerField()),
                ('nzms_ymax', models.IntegerField()),
                ('nzms_ymin', models.IntegerField()),
                ('nztm_xmax', models.FloatField()),
                ('nztm_xmin', models.FloatField()),
                ('nztm_ymax', models.FloatField()),
                ('nztm_ymin', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='OrthoSet',
            fields=[
                ('identifier', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('year_captured', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('imagelayer_uri', models.CharField(blank=True, max_length=1024, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='OrthoTile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.TextField(verbose_name='Tile id')),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=2193)),
                ('local_fname', models.CharField(blank=True, max_length=255, null=True)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiles', to='geolib.OrthoSet')),
            ],
        ),
        migrations.CreateModel(
            name='PlaceName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('status', models.TextField(blank=True, null=True)),
                ('feat_type', models.TextField(blank=True, null=True)),
                ('nzgb_ref', models.CharField(blank=True, max_length=255, null=True)),
                ('land_district', models.TextField(blank=True, null=True)),
                ('info_ref', models.TextField(blank=True, null=True)),
                ('info_origin', models.TextField(blank=True, null=True)),
                ('info_description', models.TextField(blank=True, null=True)),
                ('desc_code', models.TextField(blank=True, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='TerritorialAuthority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='Topo50_Island',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('group', models.CharField(blank=True, max_length=255, null=True)),
                ('provenance', models.TextField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='Topo50_Lake',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('category', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='Topo50_Rail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('track_type', models.CharField(blank=True, max_length=255, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiLineStringField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='Topo50_RiverLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('stream_order', models.PositiveIntegerField(blank=True, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiLineStringField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='Topo50_RiverPoly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='Topo50_Road',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('hway_num', models.CharField(blank=True, max_length=255, null=True)),
                ('lane_count', models.IntegerField(blank=True, null=True)),
                ('way_count', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(blank=True, max_length=255, null=True)),
                ('surface', models.CharField(blank=True, max_length=255, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiLineStringField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='Topo50grid',
            fields=[
                ('identifier', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('sheet_name', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=2193)),
                ('nzms_xmax', models.IntegerField()),
                ('nzms_xmin', models.IntegerField()),
                ('nzms_ymax', models.IntegerField()),
                ('nzms_ymin', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TopoContour20Metre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elevation', models.IntegerField()),
                ('provenance', models.TextField(blank=True, null=True)),
                ('topo50', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiLineStringField(srid=2193)),
            ],
        ),
        migrations.CreateModel(
            name='TopoMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('sheet_id', models.CharField(blank=True, max_length=255, null=True)),
                ('projection', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('local_fname', models.CharField(blank=True, max_length=255, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=2193)),
            ],
            options={
                'ordering': ('series', 'sheet_id'),
            },
        ),
        migrations.CreateModel(
            name='TopoMapFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('uri', models.CharField(max_length=1024)),
                ('file_format', models.CharField(max_length=255)),
                ('received', models.DateField()),
                ('received_fname', models.CharField(max_length=255)),
                ('uploaded', models.DateField(blank=True, null=True)),
                ('uploaded_by', models.CharField(blank=True, max_length=255, null=True)),
                ('provenance', models.TextField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('sheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='geolib.TopoMap')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TopoMapSeries',
            fields=[
                ('series', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('letter', models.CharField(blank=True, max_length=8, null=True)),
                ('ordinal', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('source_instution', models.CharField(max_length=255)),
                ('uri', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ('series',),
            },
        ),
        migrations.CreateModel(
            name='Waterways',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_name', models.CharField(blank=True, max_length=255, null=True)),
                ('type_name', models.CharField(blank=True, max_length=255, null=True)),
                ('label', models.CharField(blank=True, max_length=255, null=True)),
                ('provenance', models.TextField(blank=True, null=True)),
                ('geom', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=2193)),
            ],
        ),
        migrations.AddField(
            model_name='topomap',
            name='series',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sheets', to='geolib.TopoMapSeries'),
        ),
        migrations.AddField(
            model_name='aerialrun',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='runs', to='geolib.AerialSurvey'),
        ),
        migrations.AddField(
            model_name='aerialframe',
            name='run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frames', to='geolib.AerialRun'),
        ),
    ]
