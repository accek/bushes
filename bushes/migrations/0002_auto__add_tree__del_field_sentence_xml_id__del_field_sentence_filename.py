# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tree'
        db.create_table(u'bushes_tree', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assignment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bushes.Assignment'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tree_json', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'bushes', ['Tree'])

        # Deleting field 'Sentence.xml_id'
        db.delete_column(u'bushes_sentence', 'xml_id')

        # Deleting field 'Sentence.filename'
        db.delete_column(u'bushes_sentence', 'filename')

        # Adding field 'Sentence.identifier'
        db.add_column(u'bushes_sentence', 'identifier',
                      self.gf('django.db.models.fields.CharField')(default='(None)', max_length=255),
                      keep_default=False)

        # Adding field 'Assignment.latest_tree'
        db.add_column(u'bushes_assignment', 'latest_tree',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='latest_for_assignment', null=True, to=orm['bushes.Tree']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Tree'
        db.delete_table(u'bushes_tree')


        # User chose to not deal with backwards NULL issues for 'Sentence.xml_id'
        raise RuntimeError("Cannot reverse this migration. 'Sentence.xml_id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Sentence.xml_id'
        db.add_column(u'bushes_sentence', 'xml_id',
                      self.gf('django.db.models.fields.CharField')(max_length=255),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Sentence.filename'
        raise RuntimeError("Cannot reverse this migration. 'Sentence.filename' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Sentence.filename'
        db.add_column(u'bushes_sentence', 'filename',
                      self.gf('django.db.models.fields.CharField')(max_length=255),
                      keep_default=False)

        # Deleting field 'Sentence.identifier'
        db.delete_column(u'bushes_sentence', 'identifier')

        # Deleting field 'Assignment.latest_tree'
        db.delete_column(u'bushes_assignment', 'latest_tree_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'bushes.assignment': {
            'Meta': {'object_name': 'Assignment'},
            'completion_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_tree': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'latest_for_assignment'", 'null': 'True', 'to': u"orm['bushes.Tree']"}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bushes.Sentence']"}),
            'tree_json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'bushes.sentence': {
            'Meta': {'object_name': 'Sentence'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'tokens_json': ('django.db.models.fields.TextField', [], {})
        },
        u'bushes.tree': {
            'Meta': {'object_name': 'Tree'},
            'assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bushes.Assignment']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tree_json': ('django.db.models.fields.TextField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bushes']