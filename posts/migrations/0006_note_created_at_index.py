# Generated by Django 5.0 on 2024-02-08 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_alter_note_image'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='note',
            index=models.Index(fields=['created_at'], name='created_at_index'),
        ),
    ]
