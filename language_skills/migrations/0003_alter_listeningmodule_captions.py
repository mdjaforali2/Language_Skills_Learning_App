# Generated by Django 4.2.7 on 2023-11-15 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('language_skills', '0002_remove_listeningmodule_link_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listeningmodule',
            name='captions',
            field=models.FileField(blank=True, null=True, upload_to='text/'),
        ),
    ]
