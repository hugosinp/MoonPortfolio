# Generated by Django 3.2 on 2021-05-05 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0005_transaction_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('Buy', 'Buy'), ('Sell', 'Sell')], max_length=10),
        ),
    ]
