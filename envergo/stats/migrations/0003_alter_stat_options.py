# Generated by Django 3.2.6 on 2022-01-06 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_stat_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stat',
            options={'ordering': ['order'], 'verbose_name': 'Stat', 'verbose_name_plural': 'Stats'},
        ),
    ]
