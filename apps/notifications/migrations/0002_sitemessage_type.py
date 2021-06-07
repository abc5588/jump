# Generated by Django 3.1 on 2021-06-07 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitemessage',
            name='type',
            field=models.CharField(choices=[('user', 'User message'), ('system', 'Sysem message')], default='user', max_length=64),
        ),
    ]
