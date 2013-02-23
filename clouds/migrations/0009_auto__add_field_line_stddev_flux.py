# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Line.stddev_flux'
        db.add_column(u'clouds_line', 'stddev_flux',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Line.stddev_flux'
        db.delete_column(u'clouds_line', 'stddev_flux')


    models = {
        u'clouds.image': {
            'Meta': {'object_name': 'Image'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intensity': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'sidtime': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clouds.SidTime']", 'null': 'True'})
        },
        u'clouds.line': {
            'Meta': {'object_name': 'Line'},
            'average_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'realpoint_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stddev_flux': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'clouds.realpoint': {
            'Meta': {'object_name': 'RealPoint'},
            'flux': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clouds.Image']"}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clouds.Line']", 'null': 'True'}),
            'sidpoint': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clouds.SidPoint']", 'null': 'True'}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {})
        },
        u'clouds.sidpoint': {
            'Meta': {'object_name': 'SidPoint'},
            'flux': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clouds.Line']", 'null': 'True'}),
            'prev': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['clouds.SidPoint']", 'unique': 'True', 'null': 'True'}),
            'sidtime': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clouds.SidTime']"}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {})
        },
        u'clouds.sidtime': {
            'Meta': {'object_name': 'SidTime'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        }
    }

    complete_apps = ['clouds']