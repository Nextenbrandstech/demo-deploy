# Generated by Django 5.1.2 on 2024-11-04 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_first_step_adsdata_fk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='first_step_adsdata_fk',
            name='average_cpc',
        ),
        migrations.RemoveField(
            model_name='first_step_adsdata_fk',
            name='placement_type',
        ),
        migrations.AddField(
            model_name='first_step_adsdata_fk',
            name='date',
            field=models.DateField(null=True),
        ),
    ]
