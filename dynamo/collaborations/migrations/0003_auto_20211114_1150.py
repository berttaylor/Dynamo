# Generated by Django 3.2.9 on 2021-11-14 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collaborations', '0002_auto_20211106_2300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collaborationmilestone',
            name='element',
        ),
        migrations.RemoveField(
            model_name='collaborationtask',
            name='assigned_to',
        ),
        migrations.RemoveField(
            model_name='collaborationtask',
            name='completed_by',
        ),
        migrations.RemoveField(
            model_name='collaborationtask',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='collaborationtask',
            name='element',
        ),
        migrations.RemoveField(
            model_name='collaborationtask',
            name='files',
        ),
        migrations.RemoveField(
            model_name='collaborationtask',
            name='prerequisite_tasks',
        ),
        migrations.RemoveField(
            model_name='collaborationtask',
            name='tags',
        ),
        migrations.DeleteModel(
            name='CollaborationElement',
        ),
        migrations.DeleteModel(
            name='CollaborationMilestone',
        ),
        migrations.DeleteModel(
            name='CollaborationTask',
        ),
    ]
