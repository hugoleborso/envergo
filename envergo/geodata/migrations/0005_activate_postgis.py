# Generated by Django 3.2.6 on 2021-11-03 13:47

from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("geodata", "0004_alter_parcel_unique_together"),
    ]

    operations = [
        CreateExtension("postgis"),
    ]
