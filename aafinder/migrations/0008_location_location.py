# Generated by Django 2.1.4 on 2018-12-29 09:02

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aafinder', '0007_add_meeing_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]