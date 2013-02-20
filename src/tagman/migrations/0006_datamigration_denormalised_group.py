# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Tag.group_name'
        if not db.dry_run:
            for tag in orm.Tag.objects.all():
                group = orm.TagGroup.objects.get(id=tag.group_id)
                prefix = "*" if group.system else ""
                tag.group_name = "{}{}".format(prefix, group.name)
                tag.group_slug = str(group.slug)
                tag.group_is_system = group.system
                tag.save()

    def backwards(self, orm):
        raise RuntimeError("This migration is not reversible")

    models = {
        'tagman.tag': {
            'Meta': {'unique_together': "(('name', 'group'),)", 'object_name': 'Tag'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tagman.TagGroup']"}),
            'group_is_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'group_slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '100'})
        },
        'tagman.taggroup': {
            'Meta': {'object_name': 'TagGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '100'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['tagman']
