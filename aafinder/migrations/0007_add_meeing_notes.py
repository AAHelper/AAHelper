# Generated by Django 2.0.7 on 2018-07-19 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aafinder', '0006_remove_meetingtype_day_of_week'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
