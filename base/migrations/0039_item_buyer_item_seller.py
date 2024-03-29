# Generated by Django 4.1.7 on 2023-04-25 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0038_remove_item_buyer_remove_item_seller'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='buyer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='bId', to='base.account'),
        ),
        migrations.AddField(
            model_name='item',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='sId', to='base.account'),
        ),
    ]
