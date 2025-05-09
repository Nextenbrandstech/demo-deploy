# Generated by Django 5.1.2 on 2024-11-04 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_first_step_salesdata_fk_usual_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='First_step_cogs_vertical',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=255)),
                ('pid', models.CharField(max_length=255)),
                ('vertical', models.CharField(max_length=255)),
                ('mrp', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cogs_excl_gst', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'First_step_cogs_vertical',
            },
        ),
        migrations.AlterField(
            model_name='first_step_salesdata_fk',
            name='usual_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
