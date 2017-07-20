# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Name')),
                ('slug', models.SlugField(default=b'', max_length=255)),
                ('group_name', models.CharField(help_text=b'De-normalised group name', verbose_name=b'Group name', max_length=255, editable=False, blank=True)),
                ('group_slug', models.SlugField(default=b'', editable=False, max_length=255, blank=True, help_text=b'De-normalised group slug')),
                ('group_is_system', models.BooleanField(default=False, help_text=b'De-normalised group system', editable=False)),
                ('archived', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TagGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name=b'Name')),
                ('slug', models.SlugField(default=b'', max_length=255)),
                ('system', models.BooleanField(default=False, help_text=b'Set True for system groups that should not appear for general use')),
            ],
        ),
        migrations.AddField(
            model_name='tag',
            name='group',
            field=models.ForeignKey(verbose_name=b'Group', to='tagman.TagGroup'),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name', 'group')]),
        ),
    ]
