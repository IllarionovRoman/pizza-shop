# Generated by Django 3.2.9 on 2021-11-14 14:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_alter_products_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='qty',
        ),
    ]