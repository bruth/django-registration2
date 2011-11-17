# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'RegistrationProfile.activated'
        db.add_column('registration_registrationprofile', 'activated', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'RegistrationProfile.moderated'
        db.add_column('registration_registrationprofile', 'moderated', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'RegistrationProfile.moderator'
        db.add_column('registration_registrationprofile', 'moderator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='moderated_profiles', null=True, to=orm['auth.User']), keep_default=False)

        # Adding field 'RegistrationProfile.moderation_time'
        db.add_column('registration_registrationprofile', 'moderation_time', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Changing field 'RegistrationProfile.user'
        db.alter_column('registration_registrationprofile', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['auth.User']))


    def backwards(self, orm):
        
        # Deleting field 'RegistrationProfile.activated'
        db.delete_column('registration_registrationprofile', 'activated')

        # Deleting field 'RegistrationProfile.moderated'
        db.delete_column('registration_registrationprofile', 'moderated')

        # Deleting field 'RegistrationProfile.moderator'
        db.delete_column('registration_registrationprofile', 'moderator_id')

        # Deleting field 'RegistrationProfile.moderation_time'
        db.delete_column('registration_registrationprofile', 'moderation_time')

        # Changing field 'RegistrationProfile.user'
        db.alter_column('registration_registrationprofile', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'registration.registrationprofile': {
            'Meta': {'object_name': 'RegistrationProfile'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'moderation_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'moderator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'moderated_profiles'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'registration'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['registration']
