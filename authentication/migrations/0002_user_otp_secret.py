# Generated by Django 5.1.7 on 2025-03-30 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp_secret',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
