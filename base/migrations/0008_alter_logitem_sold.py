# Generated by Django 4.1.7 on 2023-03-07 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_logitem_sold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logitem',
            name='sold',
            field=models.BooleanField(default=False),
        ),
    ]
