# Generated by Django 3.2.12 on 2022-07-29 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0067_alter_criterion_required_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='criterion',
            name='criterion',
            field=models.CharField(choices=[('rainwater_runoff', "<strong>Impact sur l'écoulement des eaux pluviales</strong><br /> Seuil de déclaration\xa0: 1\xa0ha"), ('flood_zone', '<strong>Impact sur une zone inondable</strong><br /> Seuil de déclaration\xa0: 400\xa0m²'), ('wetland', '<strong>Impact sur une zone humide</strong><br /> Seuil de déclaration\xa0: 1\xa0000\xa0m²')], max_length=128, verbose_name='Criterion'),
        ),
    ]
