from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import (
    EmailMultiAlternatives,
)
from django.conf import settings
from django.template.loader import render_to_string
from wonderhop.landing.models import (
    Signup,
    Invite,
)
from createsend import Subscriber, BadRequest
import logging

@receiver(post_save, sender=Signup)
def signup_post_save_handler(sender, **kwargs):
    signup = kwargs["instance"]
    if kwargs["created"]:
        try:
            fields = { "referral_url": signup.referral_url() }
            Subscriber().add(settings.CREATESEND_SIGNUPS_LIST_ID, signup.email, "Unknown", [{"Key": k, "Value": v} for k, v in fields.iteritems()], True)
        except Exception:
            logging.exception("Exception adding user to signups email list")
        
        # Delete from the invitees list
        # Do this whether or not they used a referral link; they might be in invitees
        # even if they found WonderHop on their own.
        try:
            Subscriber(settings.CREATESEND_INVITEES_LIST_ID, signup.email).delete()
        except BadRequest as b:
            if b.data.Code == 203: # 203 means Not Found. Good work, Campaign Monitor...
                # This is normal. Usually the user has not been invited.
                pass
            else:
                logging.exception("BadRequest deleting new signup from invitees list")
        except Exception:
            logging.exception("Exception deleting new signup from invitees list")
        
        if signup.referring_user is not None:
            new_reward = None
            if signup.referring_user.incentive_plan is not None:
                new_rewards = list(signup.referring_user.incentive_plan.reward_tiers.filter(num_signups=signup.referring_user.referred_user_set.count()))
                if len(new_rewards) > 0:
                    # There should only be one, presumably
                    new_reward = new_rewards[0]
            
            params = {
                "referral_link": signup.referral_url(),
                "new_reward": new_reward,
            }
            m = EmailMultiAlternatives(
                subject="Someone you invited signed up for WonderHop",
                body=render_to_string("invite_accepted_email.txt", params),
                from_email="WonderHop <contact@wonderhop.com>", 
                to=[signup.referring_user.email],
            )
            m.attach_alternative(render_to_string("invite_accepted_email.html", params), "text/html")
            try:
                m.send()
            except Exception:
                logging.exception("Exception sending referred-user email")
