# Generated by Django 3.1.2 on 2021-02-10 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0007_paper_elapsed_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='elapsed_time',
        ),
        migrations.AddField(
            model_name='paper',
            name='publishable',
            field=models.BooleanField(default=False),
        ),
    ]
