# Generated by Django 4.0.2 on 2022-07-14 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0017_remove_student_name_remove_teacher_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=20, null=True),
        ),
    ]