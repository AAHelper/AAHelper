# Generated by Django 2.0 on 2018-07-12 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=2)),
                ('zip_code', models.CharField(max_length=5)),
                ('address_string', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('time', models.TimeField(db_index=True)),
                ('url', models.URLField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='MeetingArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MeetingCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=5)),
                ('description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MeetingType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('is_day_of_week', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='meeting',
            name='area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='aafinder.MeetingArea'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='codes',
            field=models.ManyToManyField(to='aafinder.MeetingCode'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aafinder.Location'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='types',
            field=models.ManyToManyField(to='aafinder.MeetingType'),
        ),
    ]
