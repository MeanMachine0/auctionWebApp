# Generated by Django 4.1.7 on 2023-04-19 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0033_alter_movie_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='posterUrl',
            new_name='posterURL',
        ),
    ]
