# Generated by Django 5.1.7 on 2025-04-16 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_type',
            field=models.CharField(choices=[('question', 'Question'), ('article', 'Article')], default='question', max_length=20),
        ),
    ]
