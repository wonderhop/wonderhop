from django.db import models
from decimal import Decimal

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
    referring_user = models.ForeignKey("self", null=True, blank=True, related_name="referred_user_set")
    sign_up_date = models.DateTimeField(auto_now_add=True)
    incentive_plan = models.ForeignKey(IncentivePlan, null=True, blank=True, default=lambda: LandingSettings.objects.singleton_instance().default_incentive_plan)

    def __unicode__(self):
        return self.email

    def reward_balance(self):
        """Returns the user's current reward balance as a decimal.Decimal."""
        if self.incentive_plan is None: return Decimal(0)
        
        referring_user_plan = None if self.referring_user is None else self.referring_user.incentive_plan
        invitee_incentive = 0 if referring_user_plan is None else referring_user_plan.invitee_incentive
        
        num_referred_users = self.referred_user_set.count()
        return self.incentive_plan.reward_tiers.filter(
            num_signups__lte=num_referred_users
        ).aggregate(
            reward_balance=models.Sum("reward")
        )["reward_balance"] + invitee_incentive

class SingletonManager(models.Manager):
    def singleton_instance(self):
        return self.get_or_create(id=0)[0]

class LandingSettings(models.Model):
    id = models.IntegerField(primary_key=True, choices=((0, "Default"),), default=0)
    default_incentive_plan = models.ForeignKey(IncentivePlan, null=True, blank=True)

    objects = SingletonManager()

    class Meta:
        verbose_name_plural = "Landing Settings"
