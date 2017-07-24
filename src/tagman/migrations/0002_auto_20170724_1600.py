# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def denormalised_group(apps, schema_editor):
    Tag = apps.get_model('tagman', 'Tag')
    TagGroup = apps.get_model('tagman', 'TagGroup')

    for tag in Tag.objects.all():
        group = TagGroup.objects.get(id=tag.group_id)
        prefix = "*" if group.system else ""
        tag.group_name = "{}{}".format(prefix, group.name)
        tag.group_slug = str(group.slug)
        tag.group_is_system = group.system
        tag.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tagman', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(denormalised_group)
    ]
