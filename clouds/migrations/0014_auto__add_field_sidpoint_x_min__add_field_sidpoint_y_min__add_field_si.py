# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SidPoint.x_min'
        db.add_column('clouds_sidpoint', 'x_min',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'SidPoint.y_min'
        db.add_column('clouds_sidpoint', 'y_min',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'SidPoint.width'
        db.add_column('clouds_sidpoint', 'width',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'SidPoint.height'
        db.add_column('clouds_sidpoint', 'height',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'RealPoint.x_min'
        db.add_column('clouds_realpoint', 'x_min',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'RealPoint.y_min'
        db.add_column('clouds_realpoint', 'y_min',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'RealPoint.width'
        db.add_column('clouds_realpoint', 'width',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'RealPoint.height'
        db.add_column('clouds_realpoint', 'height',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SidPoint.x_min'
        db.delete_column('clouds_sidpoint', 'x_min')

        # Deleting field 'SidPoint.y_min'
        db.delete_column('clouds_sidpoint', 'y_min')

        # Deleting field 'SidPoint.width'
        db.delete_column('clouds_sidpoint', 'width')

        # Deleting field 'SidPoint.height'
        db.delete_column('clouds_sidpoint', 'height')

        # Deleting field 'RealPoint.x_min'
        db.delete_column('clouds_realpoint', 'x_min')

        # Deleting field 'RealPoint.y_min'
        db.delete_column('clouds_realpoint', 'y_min')

        # Deleting field 'RealPoint.width'
        db.delete_column('clouds_realpoint', 'width')

        # Deleting field 'RealPoint.height'
        db.delete_column('clouds_realpoint', 'height')


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
        'clouds.sidpoint': {
            'Meta': {'ordering': "['sidtime__time']", 'unique_together': "(('sidtime', 'idx'),)", 'object_name': 'SidPoint'},
            'flux': ('django.db.models.fields.FloatField', [], {}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Line']", 'null': 'True'}),
            'prev': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['clouds.SidPoint']", 'unique': 'True', 'null': 'True'}),
            'sidtime': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.SidTime']"}),
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