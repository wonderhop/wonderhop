# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LandingSettings'
        db.create_table('landing_landingsettings', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('default_incentive_plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['landing.IncentivePlan'], null=True, blank=True)),
        ))
        db.send_create_signal('landing', ['LandingSettings'])


    def backwards(self, orm):
        
        # Deleting model 'LandingSettings'
        db.delete_table('landing_landingsettings')


    models = {
        'landing.incentiveplan': {
            'Meta': {'object_name': 'IncentivePlan'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invitee_incentive': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'landing.incentiveplanrewardtier': {
            'Meta': {'object_name': 'IncentivePlanRewardTier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incentive_plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reward_tiers'", 'to': "orm['landing.IncentivePlan']"}),
            'num_signups': ('django.db.models.fields.IntegerField', [], {}),
            'reward': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'landing.landingsettings': {
            'Meta': {'object_name': 'LandingSettings'},
            'default_incentive_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['landing.IncentivePlan']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'landing.signup': {
            'Meta': {'object_name': 'Signup'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incentive_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['landing.IncentivePlan']", 'null': 'True', 'blank': 'True'}),
            'referral_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'referring_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'referred_user_set'", 'null': 'True', 'to': "orm['landing.Signup']"}),
            'sign_up_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['landing']
