# Generated by Django 4.0.6 on 2024-03-18 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0004_booking_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='price',
        ),
        migrations.AddField(
            model_name='ground',
            name='price',
            field=models.DecimalField(decimal_places=2, default=11, max_digits=8),
            preserve_default=False,
        ),
    ]