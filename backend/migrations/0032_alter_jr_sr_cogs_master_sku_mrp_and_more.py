# Generated by Django 5.1.3 on 2024-12-04 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0031_alter_jr_sr_cogs_master_sku_mrp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jr_sr_cogs_master_sku',
            name='mrp',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='jr_sr_cogs_master_sku',
            name='pack_size',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='jr_sr_cogs_master_sku',
            name='settlement_per_unit',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='jr_sr_cogs_master_sku',
            name='total_cogs',
            field=models.CharField(max_length=100),
        ),
    ]
