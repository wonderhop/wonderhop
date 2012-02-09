from django.db import models

class Signup(models.Model):
    email = models.EmailField(unique=True)
    referral_key = models.CharField(unique=True, max_length=16)

    def __unicode__(self):
        return self.email
