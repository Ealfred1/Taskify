# Generated by Django 4.2.8 on 2024-04-03 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_task_reminder_alter_task_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='reminder',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
