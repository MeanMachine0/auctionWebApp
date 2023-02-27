# Generated by Django 4.1.7 on 2023-02-24 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('startingPrice', models.DecimalField(decimal_places=2, max_digits=10)),
                ('postageCost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bidIncrement', models.DecimalField(decimal_places=2, max_digits=10)),
                ('condition', models.CharField(choices=[('new', 'New'), ('excellent', 'Excellent'), ('good', 'Good'), ('used', 'Used'), ('refurbished', 'Refurbished'), ('partsOnly', 'Parts Only')], max_length=20)),
                ('endDateTime', models.DateTimeField()),
                ('acceptReturns', models.BooleanField(default=False)),
                ('description', models.TextField()),
            ],
        ),
    ]
