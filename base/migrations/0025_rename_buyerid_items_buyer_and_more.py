# Generated by Django 4.1.7 on 2023-04-11 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_delete_endeditems_items_destinationaddress_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='items',
            old_name='buyerId',
            new_name='buyer',
        ),
        migrations.RenameField(
            model_name='items',
            old_name='sellerId',
            new_name='seller',
        ),
    ]
