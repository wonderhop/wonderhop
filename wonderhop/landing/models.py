from django.db import models

class IncentivePlan(models.Model):
    invitee_incentive = models.DecimalField(max_digits=6, decimal_places=2)
    name = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.name

class IncentivePlanRewardTier(models.Model):
    incentive_plan = models.ForeignKey(IncentivePlan, related_name="reward_tiers")
    num_signups = models.IntegerField()
    reward = models.DecimalField(max_digits=6, decimal_places=2)

    def __unicode__(self):
        return "{0} signups gives ${1}".format(self.num_signups, self.reward)

class Signup(models.Model):
    email = models.EmailField(unique=True)
    referral_key = models.CharField(unique=True, max_length=16)
    referring_user = models.ForeignKey("self", null=True, blank=True)
    sign_up_date = models.DateTimeField(auto_now_add=True)
    incentive_plan = models.ForeignKey(IncentivePlan, null=True, blank=True)

    def __unicode__(self):
        return self.email
