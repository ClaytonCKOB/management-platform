# Generated by Django 4.0.5 on 2022-07-18 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_remove_item_ambiente_item_altcom_item_peso_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='client',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='order',
            name='id_pipe',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
