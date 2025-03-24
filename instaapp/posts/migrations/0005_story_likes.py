# Generated by Django 5.1.7 on 2025-03-24 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_story'),
        ('profiles', '0004_alter_profile_followers'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_stories', to='profiles.profile'),
        ),
    ]
