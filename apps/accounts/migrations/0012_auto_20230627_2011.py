# Generated by Django 3.2.19 on 2023-06-27 12:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20230506_1443'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProtocolConfig',
            fields=[
                ('created_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='Created by')),
                ('updated_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='Updated by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('comment', models.TextField(blank=True, default='', verbose_name='Comment')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('org_id', models.CharField(blank=True, db_index=True, default='', max_length=36, verbose_name='Organization')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('protocol', models.CharField(max_length=128, verbose_name='Protocol')),
                ('setting', models.JSONField(default=dict, verbose_name='Setting')),
            ],
            options={
                'verbose_name': 'Protocol Config',
                'ordering': ('name',),
                'unique_together': {('org_id', 'name')},
            },
        ),
        migrations.CreateModel(
            name='AccountTemplateProtocolConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('account_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='protocol_settings', to='accounts.accounttemplate')),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_template_settings', to='accounts.protocolconfig')),
            ],
            options={
                'unique_together': {('account_template', 'config')},
            },
        ),
        migrations.CreateModel(
            name='AccountProtocolConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='protocol_settings', to='accounts.account')),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_settings', to='accounts.protocolconfig')),
            ],
            options={
                'unique_together': {('account', 'config')},
            },
        ),
        migrations.AddField(
            model_name='account',
            name='configs',
            field=models.ManyToManyField(related_name='accounts', through='accounts.AccountProtocolConfig', to='accounts.ProtocolConfig'),
        ),
        migrations.AddField(
            model_name='accounttemplate',
            name='configs',
            field=models.ManyToManyField(related_name='account_templates', through='accounts.AccountTemplateProtocolConfig', to='accounts.ProtocolConfig'),
        ),
    ]
