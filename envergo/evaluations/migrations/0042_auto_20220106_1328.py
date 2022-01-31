# Generated by Django 3.2.6 on 2022-01-06 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0041_auto_20211108_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='criterion',
            name='result',
            field=models.IntegerField(choices=[(1, 'Subject to LSE'), (2, 'Non subject to LSE'), (3, 'Action required')], null=True, verbose_name='Result'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='result',
            field=models.IntegerField(choices=[(1, 'Subject to LSE'), (2, 'Non subject to LSE'), (3, 'Action required')], null=True, verbose_name='Result'),
        ),
    ]
