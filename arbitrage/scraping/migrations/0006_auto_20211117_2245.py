# Generated by Django 3.2.9 on 2021-11-17 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0005_user_search_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='result_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='file_upload_count',
            field=models.IntegerField(default=0),
        ),
    ]
