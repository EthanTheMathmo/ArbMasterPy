# Generated by Django 3.2.9 on 2021-11-18 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0006_auto_20211117_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='web_address',
            field=models.CharField(default='www.google.com', max_length=512),
            preserve_default=False,
        ),
    ]