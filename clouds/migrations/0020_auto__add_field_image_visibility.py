# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Image.visibility'
        db.add_column('clouds_image', 'visibility',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Image.visibility'
        db.delete_column('clouds_image', 'visibility')


    models = {
        'clouds.image': {
            'Meta': {'object_name': 'Image'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intensity': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'sidtime': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.SidTime']", 'null': 'True'}),
            'visibility': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        'clouds.line': {
            'Meta': {'object_name': 'Line'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clouds.linevalues': {
            'Meta': {'unique_together': "(('line', 'generation'),)", 'object_name': 'LineValues'},
            'average_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'generation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.LineValuesGeneration']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Line']"}),
            'max_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'realpoint_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sidpoint_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stddev_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'clouds.linevaluesgeneration': {
            'Meta': {'object_name': 'LineValuesGeneration'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clouds.realpoint': {
            'Meta': {'ordering': "['image__datetime']", 'object_name': 'RealPoint'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'flux': ('django.db.models.fields.FloatField', [], {}),
            'flux_error': ('django.db.models.fields.FloatField', [], {}),
            'generation': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['clouds.RealPointGeneration']"}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Image']"}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Line']", 'null': 'True'}),
            'sidpoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.SidPoint']", 'null': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'x_min': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {}),
            'y_min': ('django.db.models.fields.FloatField', [], {})
        },
        'clouds.realpointgeneration': {
            'Meta': {'object_name': 'RealPointGeneration'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clouds.sidpoint': {
            'Meta': {'ordering': "['sidtime__time']", 'unique_together': "(('sidtime', 'idx'),)", 'object_name': 'SidPoint'},
            'flux': ('django.db.models.fields.FloatField', [], {}),
            'flux_error': ('django.db.models.fields.FloatField', [], {}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Line']", 'null': 'True'}),
            'prev': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['clouds.SidPoint']", 'unique': 'True', 'null': 'True'}),
            'sidtime': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.SidTime']"}),
            'step': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'x_min': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {}),
            'y_min': ('django.db.models.fields.FloatField', [], {})
        },
        'clouds.sidtime': {
            'Meta': {'object_name': 'SidTime'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['clouds']