# Generated by Django 5.0.3 on 2024-06-02 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0026_thought"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="availableWorkingHours",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="description",
            field=models.CharField(blank=True, max_length=1500, null=True),
        ),
    ]
