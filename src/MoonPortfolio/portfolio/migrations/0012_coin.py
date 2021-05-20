# Generated by Django 3.2 on 2021-05-20 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0011_delete_coin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('symbol', models.CharField(max_length=5)),
                ('current_price', models.FloatField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('market_cap', models.FloatField(default=0)),
                ('image', models.URLField()),
                ('price_change_24h', models.FloatField(blank=True, default=0, null=True)),
                ('circulating_supply', models.FloatField(blank=True, default=0, null=True)),
                ('total_supply', models.FloatField(blank=True, default=0, null=True)),
                ('ath', models.FloatField(blank=True, default=0, null=True)),
                ('atl', models.FloatField(blank=True, default=0, null=True)),
            ],
        ),
    ]
