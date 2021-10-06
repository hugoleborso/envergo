# Generated by Django 3.2.6 on 2021-10-06 09:25

from django.db import migrations, models
import envergo.evaluations.models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0029_auto_20211005_0946'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='additional_data',
            field=models.FileField(blank=True, null=True, upload_to=envergo.evaluations.models.additional_data_file_format, verbose_name='Additional data'),
        ),
    ]
