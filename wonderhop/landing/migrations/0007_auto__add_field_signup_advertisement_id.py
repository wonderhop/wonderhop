# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Signup.advertisement_id'
        db.add_column('landing_signup', 'advertisement_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Signup.advertisement_id'
        db.delete_column('landing_signup', 'advertisement_id')


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
        'landing.invite': {
            'Meta': {'object_name': 'Invite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_invites_set'", 'to': "orm['landing.Signup']"}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'landing.landingsettings': {
            'Meta': {'object_name': 'LandingSettings'},
            'default_incentive_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['landing.IncentivePlan']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'primary_key': 'True'})
        },
        'landing.signup': {
            'Meta': {'object_name': 'Signup'},
            'advertisement_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incentive_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['landing.IncentivePlan']", 'null': 'True', 'blank': 'True'}),
            'referral_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'referring_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'referred_user_set'", 'null': 'True', 'to': "orm['landing.Signup']"}),
            'sign_up_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['landing']
