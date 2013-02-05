# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Image.intensity'
        db.add_column('clouds_image', 'intensity',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Image.intensity'
        db.delete_column('clouds_image', 'intensity')


    models = {
        'clouds.image': {
            'Meta': {'object_name': 'Image'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intensity': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'})
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