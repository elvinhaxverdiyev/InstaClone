# Generated by Django 5.1.7 on 2025-04-02 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='verification_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
