# Generated by Django 4.1.7 on 2023-03-08 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_endeditems_bidders_items_bidders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endeditems',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='items',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]