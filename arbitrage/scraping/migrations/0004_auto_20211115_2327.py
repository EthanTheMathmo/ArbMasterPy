# Generated by Django 3.2.9 on 2021-11-15 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0003_blacklist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='result',
            old_name='price',
            new_name='retailer_price',
        ),
        migrations.AddField(
            model_name='result',
            name='asin',
            field=models.CharField(default=0.0, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='result',
            name='target_price',
            field=models.DecimalField(decimal_places=8, default=0.0, max_digits=32),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='result',
            name='url',
            field=models.CharField(max_length=512),
        ),
    ]
