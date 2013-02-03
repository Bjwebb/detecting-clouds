# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SidTime'
        db.create_table('clouds_sidtime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('clouds', ['SidTime'])

        # Adding model 'Line'
        db.create_table('clouds_line', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('clouds', ['Line'])

        # Adding model 'SidPoint'
        db.create_table('clouds_sidpoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('x', self.gf('django.db.models.fields.FloatField')()),
            ('y', self.gf('django.db.models.fields.FloatField')()),
            ('flux', self.gf('django.db.models.fields.FloatField')()),
            ('line', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clouds.Line'])),
            ('idx', self.gf('django.db.models.fields.IntegerField')()),
            ('sidtime', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clouds.SidTime'])),
            ('prev', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['clouds.SidPoint'], unique=True, null=True)),
        ))
        db.send_create_signal('clouds', ['SidPoint'])

        # Adding model 'Image'
        db.create_table('clouds_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('clouds', ['Image'])

        # Adding model 'RealPoint'
        db.create_table('clouds_realpoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('x', self.gf('django.db.models.fields.FloatField')()),
            ('y', self.gf('django.db.models.fields.FloatField')()),
            ('flux', self.gf('django.db.models.fields.FloatField')()),
            ('line', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clouds.Line'])),
            ('idx', self.gf('django.db.models.fields.IntegerField')()),
            ('sidpoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clouds.SidPoint'])),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clouds.Image'])),
        ))
        db.send_create_signal('clouds', ['RealPoint'])


    def backwards(self, orm):
        # Deleting model 'SidTime'
        db.delete_table('clouds_sidtime')

        # Deleting model 'Line'
        db.delete_table('clouds_line')

        # Deleting model 'SidPoint'
        db.delete_table('clouds_sidpoint')

        # Deleting model 'Image'
        db.delete_table('clouds_image')

        # Deleting model 'RealPoint'
        db.delete_table('clouds_realpoint')


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
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Line']"}),
            'sidpoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.SidPoint']"}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {})
        },
        'clouds.sidpoint': {
            'Meta': {'object_name': 'SidPoint'},
            'flux': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clouds.Line']"}),
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