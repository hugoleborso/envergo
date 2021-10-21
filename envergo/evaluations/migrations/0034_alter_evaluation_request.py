# Generated by Django 3.2.6 on 2021-10-11 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0033_copy_contact_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='request',
            field=models.OneToOneField(blank=True, help_text='Does this evaluation answers to an existing request?', null=True, on_delete=django.db.models.deletion.SET_NULL, to='evaluations.request', verbose_name='Request'),
        ),
    ]
