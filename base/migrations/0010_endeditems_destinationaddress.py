# Generated by Django 4.1.7 on 2023-03-07 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_endeditems_delete_logitem_alter_accounts_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='endeditems',
            name='destinationAddress',
            field=models.CharField(default="42 Queen's Street", max_length=40),
        ),
    ]
