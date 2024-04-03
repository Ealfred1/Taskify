# Generated by Django 4.2.8 on 2024-04-03 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_task_status_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='reminder',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('todo', 'To-Do'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='todo', max_length=20),
        ),
    ]
