# Generated by Django 5.1.7 on 2025-05-20 02:42

import community.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0003_alter_post_audio_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to=community.models.Post.user_directory_path),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=community.models.Post.user_directory_path),
        ),
    ]
