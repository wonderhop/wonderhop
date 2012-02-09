# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Signup.referral_key'
        db.add_column('landing_signup', 'referral_key', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=16), keep_default=False)

        # Adding unique constraint on 'Signup', fields ['email']
        db.create_unique('landing_signup', ['email'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Signup', fields ['email']
        db.delete_unique('landing_signup', ['email'])

        # Deleting field 'Signup.referral_key'
        db.delete_column('landing_signup', 'referral_key')


    models = {
        'landing.signup': {
            'Meta': {'object_name': 'Signup'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referral_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        }
    }

    complete_apps = ['landing']
