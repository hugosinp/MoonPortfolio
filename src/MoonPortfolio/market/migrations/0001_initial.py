# Generated by Django 3.2 on 2021-04-20 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Crypto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('symbol', models.CharField(max_length=200)),
                ('image', models.URLField()),
                ('price', models.CharField(max_length=200)),
                ('rank', models.CharField(max_length=10)),
                ('market_cap', models.CharField(max_length=200)),
            ],
        ),
    ]