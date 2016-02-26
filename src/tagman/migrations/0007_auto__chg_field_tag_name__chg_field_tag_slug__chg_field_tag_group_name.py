# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Tag.name'
        db.alter_column('tagman_tag', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Tag.slug'
        db.alter_column('tagman_tag', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=255))

        # Changing field 'Tag.group_name'
        db.alter_column('tagman_tag', 'group_name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Tag.group_slug'
        db.alter_column('tagman_tag', 'group_slug', self.gf('django.db.models.fields.SlugField')(max_length=255))

        # Changing field 'TagGroup.name'
        db.alter_column('tagman_taggroup', 'name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255))

        # Changing field 'TagGroup.slug'
        db.alter_column('tagman_taggroup', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=255))

    def backwards(self, orm):

        # Changing field 'Tag.name'
        db.alter_column('tagman_tag', 'name', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Tag.slug'
        db.alter_column('tagman_tag', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=100))

        # Changing field 'Tag.group_name'
        db.alter_column('tagman_tag', 'group_name', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Tag.group_slug'
        db.alter_column('tagman_tag', 'group_slug', self.gf('django.db.models.fields.SlugField')(max_length=100))

        # Changing field 'TagGroup.name'
        db.alter_column('tagman_taggroup', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True))

        # Changing field 'TagGroup.slug'
        db.alter_column('tagman_taggroup', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=100))

    models = {
        'tagman.tag': {
            'Meta': {'unique_together': "(('name', 'group'),)", 'object_name': 'Tag'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tagman.TagGroup']"}),
            'group_is_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group_slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255'})
        },
        'tagman.taggroup': {
            'Meta': {'object_name': 'TagGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['tagman']