# Generated by Django 3.2.9 on 2021-11-27 18:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0010_customer_orders'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='slug',
            field=models.SlugField(default=uuid.uuid1, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default='В ожидании', max_length=100),
        ),
    ]