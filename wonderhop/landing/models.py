from django.db import models

class Signup(models.Model):
    email = models.EmailField(unique=True)
    referral_key = models.CharField(unique=True, max_length=16)
    referring_user = models.ForeignKey("self", null=True, blank=True)
    sign_up_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.email
