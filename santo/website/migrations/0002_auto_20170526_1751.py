# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-26 17:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Producao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(auto_now_add=True)),
                ('quantidade', models.IntegerField()),
                ('produto_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Produto')),
            ],
            options={
                'db_table': 'produção',
            },
        ),
        migrations.DeleteModel(
            name='Material',
        ),
        migrations.AddField(
            model_name='ingrediente',
            name='estoque',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingrediente',
            name='prazo_compra',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingrediente',
            name='preco_medio',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingrediente',
            name='total_comprado',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingrediente',
            name='ultima_compra',
            field=models.DateField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingrediente',
            name='valor_comprado',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
