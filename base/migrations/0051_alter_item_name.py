# Generated by Django 4.1.7 on 2023-05-05 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0050_alter_imdb_directors_alter_imdb_writers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(max_length=60),
        ),
    ]
