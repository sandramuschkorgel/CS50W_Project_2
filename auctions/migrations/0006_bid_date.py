# Generated by Django 3.1.1 on 2020-10-23 13:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_listing_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]