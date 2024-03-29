# Generated by Django 4.1.7 on 2023-04-19 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_remove_items_imagename'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(decimal_places=1, max_digits=4)),
                ('gross', models.CharField(max_length=300)),
                ('posterUrl', models.CharField(max_length=300)),
            ],
        ),
    ]
