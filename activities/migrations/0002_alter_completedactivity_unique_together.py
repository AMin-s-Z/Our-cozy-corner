# Generated by Django 5.2.4 on 2025-07-12 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("activities", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="completedactivity",
            unique_together=set(),
        ),
    ]
