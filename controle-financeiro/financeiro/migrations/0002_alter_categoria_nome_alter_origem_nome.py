# Generated by Django 5.0.2 on 2024-02-27 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='nome',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='origem',
            name='nome',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
