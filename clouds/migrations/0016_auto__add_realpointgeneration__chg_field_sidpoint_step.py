# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RealPointGeneration'
        db.create_table('clouds_realpointgeneration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('clouds', ['RealPointGeneration'])


        # Changing field 'SidPoint.step'
        db.alter_column('clouds_sidpoint', 'step', self.gf('django.db.models.fields.IntegerField')(null=True))

    def backwards(self, orm):
        # Deleting model 'RealPointGeneration'
        db.delete_table('clouds_realpointgeneration')


        # Changing field 'SidPoint.step'
        db.alter_column('clouds_sidpoint', 'step', self.gf('django.db.models.fields.IntegerField')())

    models = {
        'clouds.image': {
            'Meta': {'object_name': 'Image'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intensity': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'sidtime': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.SidTime']", 'null': 'True'})
        },
        'clouds.line': {
            'Meta': {'object_name': 'Line'},
            'average_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'realpoint_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sidpoint_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stddev_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'clouds.realpoint': {
            'Meta': {'ordering': "['image__datetime']", 'object_name': 'RealPoint'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'flux': ('django.db.models.fields.FloatField', [], {}),
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