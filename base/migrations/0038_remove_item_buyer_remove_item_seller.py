# Generated by Django 4.1.7 on 2023-04-25 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0037_rename_accounts_account_rename_items_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='buyer',
        ),
        migrations.RemoveField(
            model_name='item',
            name='seller',
        ),
    ]