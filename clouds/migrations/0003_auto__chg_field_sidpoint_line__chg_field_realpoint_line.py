# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'SidPoint.line'
        db.alter_column('clouds_sidpoint', 'line_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clouds.Line'], null=True))

        # Changing field 'RealPoint.line'
        db.alter_column('clouds_realpoint', 'line_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clouds.Line'], null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'SidPoint.line'
        raise RuntimeError("Cannot reverse this migration. 'SidPoint.line' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RealPoint.line'
        raise RuntimeError("Cannot reverse this migration. 'RealPoint.line' and its values cannot be restored.")

    models = {
        'clouds.image': {
            'Meta': {'object_name': 'Image'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clouds.line': {
            'Meta': {'object_name': 'Line'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clouds.realpoint': {
            'Meta': {'object_name': 'RealPoint'},
            'flux': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Image']"}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Line']", 'null': 'True'}),
            'sidpoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.SidPoint']", 'null': 'True'}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {})
        },
        'clouds.sidpoint': {
            'Meta': {'object_name': 'SidPoint'},
            'flux': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Line']", 'null': 'True'}),
            'prev': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['clouds.SidPoint']", 'unique': 'True', 'null': 'True'}),
            'sidtime': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.SidTime']"}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {})
        },
        'clouds.sidtime': {
            'Meta': {'object_name': 'SidTime'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        }
    }

    complete_apps = ['clouds']