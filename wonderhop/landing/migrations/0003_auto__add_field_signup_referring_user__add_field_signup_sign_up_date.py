# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Signup.referring_user'
        db.add_column('landing_signup', 'referring_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['landing.Signup'], null=True, blank=True), keep_default=False)

        # Adding field 'Signup.sign_up_date'
        db.add_column('landing_signup', 'sign_up_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2012, 2, 9, 19, 30, 43, 364762), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Signup.referring_user'
        db.delete_column('landing_signup', 'referring_user_id')

        # Deleting field 'Signup.sign_up_date'
        db.delete_column('landing_signup', 'sign_up_date')


    models = {
        'landing.signup': {
            'Meta': {'object_name': 'Signup'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referral_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'referring_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['landing.Signup']", 'null': 'True', 'blank': 'True'}),
            'sign_up_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['landing']
