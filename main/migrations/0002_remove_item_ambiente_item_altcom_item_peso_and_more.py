# Generated by Django 4.0.5 on 2022-07-18 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='ambiente',
        ),
        migrations.AddField(
            model_name='item',
            name='altCom',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='item',
            name='peso',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='id_pipe',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='item',
            name='altura',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='item',
            name='largura',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='item',
            name='pos',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='item',
            name='quant',
            field=models.IntegerField(),
        ),
    ]
