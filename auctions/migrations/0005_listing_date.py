# Generated by Django 3.1.1 on 2020-10-23 13:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20201020_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
