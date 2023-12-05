# Generated by Django 2.1.7 on 2019-02-28 10:16

import assets.models.asset
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [('assets', '0002_auto_20180105_1807'), ('assets', '0003_auto_20180109_2331'), ('assets', '0004_auto_20180125_1218'), ('assets', '0005_auto_20180126_1637'), ('assets', '0006_auto_20180130_1502'), ('assets', '0007_auto_20180225_1815'), ('assets', '0008_auto_20180306_1804'), ('assets', '0009_auto_20180307_1212')]

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adminuser',
            options={'ordering': ['name'], 'verbose_name': 'Admin user'},
        ),
        migrations.AlterModelOptions(
            name='asset',
            options={'verbose_name': 'Asset'},
        ),
        migrations.AlterModelOptions(
            name='assetgroup',
            options={'ordering': ['name'], 'verbose_name': 'Asset group'},
        ),
        migrations.AlterModelOptions(
            name='cluster',
            options={'ordering': ['name'], 'verbose_name': 'Cluster'},
        ),
        migrations.AlterModelOptions(
            name='systemuser',
            options={'ordering': ['name'], 'verbose_name': 'System user'},
        ),
        migrations.RemoveField(
            model_name='asset',
            name='cluster',
        ),
        migrations.AlterField(
            model_name='assetgroup',
            name='created_by',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by'),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('value', models.CharField(max_length=128, verbose_name='Value')),
                ('category', models.CharField(choices=[('S', 'System'), ('U', 'User')], default='U', max_length=128, verbose_name='Category')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
            ],
            options={
                'db_table': 'assets_label',
            },
        ),
        migrations.AlterUniqueTogether(
            name='label',
            unique_together={('name', 'value')},
        ),
        migrations.AddField(
            model_name='asset',
            name='labels',
            field=models.ManyToManyField(blank=True, related_name='assets', to='assets.Label', verbose_name='Labels'),
        ),
        migrations.RemoveField(
            model_name='asset',
            name='cabinet_no',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='cabinet_pos',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='env',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='remote_card_ip',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='status',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='type',
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=64, unique=True, verbose_name='Key')),
                ('value', models.CharField(max_length=128, verbose_name='Value')),
                ('child_mark', models.IntegerField(default=0)),
                ('date_create', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='asset',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='systemuser',
            name='cluster',
        ),
        migrations.AlterField(
            model_name='asset',
            name='admin_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.AdminUser', verbose_name='Admin user'),
        ),
        migrations.AlterField(
            model_name='systemuser',
            name='protocol',
            field=models.CharField(choices=[('ssh', 'ssh'), ('rdp', 'rdp')], default='ssh', max_length=16, verbose_name='Protocol'),
        ),
        migrations.AddField(
            model_name='asset',
            name='nodes',
            field=models.ManyToManyField(default=assets.models.asset.default_node, related_name='assets', to='assets.Node', verbose_name='Node'),
        ),
        migrations.AddField(
            model_name='systemuser',
            name='nodes',
            field=models.ManyToManyField(blank=True, to='assets.Node', verbose_name='Nodes'),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='created_by',
            field=models.CharField(max_length=128, null=True, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='username',
            field=models.CharField(max_length=128, verbose_name='Username'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='platform',
            field=models.CharField(choices=[('Linux', 'Linux'), ('Unix', 'Unix'), ('MacOS', 'MacOS'), ('BSD', 'BSD'), ('Windows', 'Windows'), ('Other', 'Other')], default='Linux', max_length=128, verbose_name='Platform'),
        ),
        migrations.AlterField(
            model_name='systemuser',
            name='created_by',
            field=models.CharField(max_length=128, null=True, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='systemuser',
            name='username',
            field=models.CharField(max_length=128, verbose_name='Username'),
        ),
    ]
