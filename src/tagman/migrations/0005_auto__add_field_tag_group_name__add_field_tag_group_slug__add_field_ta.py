# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Tag.group_name'
        db.add_column('tagman_tag', 'group_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'Tag.group_slug'
        db.add_column('tagman_tag', 'group_slug',
                      self.gf('django.db.models.fields.SlugField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'Tag.group_is_system'
        db.add_column('tagman_tag', 'group_is_system',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Tag.group_name'
        db.delete_column('tagman_tag', 'group_name')

        # Deleting field 'Tag.group_slug'
        db.delete_column('tagman_tag', 'group_slug')

        # Deleting field 'Tag.group_is_system'
        db.delete_column('tagman_tag', 'group_is_system')


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