# Generated by Django 3.1.1 on 2020-10-20 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20201020_1922'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='listings',
        ),
        migrations.AddField(
            model_name='watchlist',
            name='item',
            field=models.ManyToManyField(to='auctions.Listing'),
        ),
    ]