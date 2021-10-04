# Generated by Django 3.2.6 on 2021-09-24 08:44

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0024_auto_20210924_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='application_number',
            field=models.CharField(blank=True, max_length=15, unique=True, validators=[django.core.validators.RegexValidator(flags=re.RegexFlag['IGNORECASE'], message='The application number format is invalid.', regex='^(PC|PA)(?P<department>\\d{3})(?P<commune>\\d{3})(?P<year>\\d{2})(?P<file>[\\w\\d]{5})$')], verbose_name='Application number'),
        ),
    ]
