from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.mail import (
    EmailMessage,
    EmailMultiAlternatives,
    get_connection,
)
from django.views.decorators.http import require_POST
from wonderhop.landing.models import (
    Signup,
    Invite,
    IncentivePlanRewardTier,
)
import random
import string
import logging
from urllib import urlencode
from createsend import Subscriber

def _id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))

def home(request):
    context = {}
    if request.method == "POST":
        try:
            email = request.POST.get("email", "").strip()
            try:
                referring_user = Signup.objects.get(referral_key=request.session.get("referral_key", None))
            except Signup.DoesNotExist:
                referring_user = None
            
            try:
                signup = Signup.objects.get(email=email)
            except Signup.DoesNotExist:
                signup = Signup(
                    email=email,
                    referring_user=referring_user,
                    advertisement_id=request.session.get("advertisement_id", None),
                    backstretch_url=request.POST.get("backstretch_url", None),
                )
                # Validate the email field, raise ValidationError if it fails
                signup.clean_fields(exclude=["referral_key"])
                MAX_ATTEMPTS = 5
                for attempt in xrange(MAX_ATTEMPTS):
                    try:
                        signup.referral_key = _id_generator()
                        signup.save()
                    except IntegrityError:
                        if attempt == MAX_ATTEMPTS - 1:
                            raise
                    else:
                        break
                
            return redirect(explanation, signup.id)
        except ValidationError as v:
            context["error"] = "Invalid email address"
    
    for track_event in ["advertisement_id", "referral_key"]:
        tracked_key = "tracked_{0}".format(track_event)
        if track_event in request.session and tracked_key not in request.session:
            context["event_{0}".format(track_event)] = request.session[track_event]
            request.session[tracked_key] = True
    
    return render(request, "signup.html", context)

def login(request):
    context = {}
    if request.method == "POST":
        try:
            signup = Signup.objects.get(email=request.POST.get("email", "").strip())
            return redirect(welcome, signup.id)
        except (ValidationError, Signup.DoesNotExist):
            context["error"] = "You're not a member yet."
    
    return render(request, "login.html", context)

def explanation(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    if signup.email is not None:
        return render(request, "explanation.html", {"signup":signup})
    
def welcome(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    REFERRAL_LINK_TEXT = "Join me on WonderHop for up to 60% off unique decor, kitchen treats, and family finds to make life one-of-a-kind."
    
    if signup.incentive_plan is None:
        reward_tiers = []
        max_reward_tier_signups = 1
    else:
        reward_tiers = list(signup.incentive_plan.reward_tiers.order_by("num_signups").all())
        max_reward_tier_signups = reward_tiers[-1].num_signups
    
    invited_users = []
    invited_emails = set() # Don't show duplicate invites
    for invite in signup.sent_invites_set.order_by("-sent_date").all():
        if invite.recipient in invited_emails: continue
        try:
            invite_signup = Signup.objects.get(email=invite.recipient)
            if invite_signup.referring_user == signup:
                description, description_class = "Signed up!", "signed_up"
            else:
                description, description_class = "Signed up from someone else's invite", "signed_up_other"
        except Signup.DoesNotExist:
            description, description_class = "Invited, Not Joined", "not_signed_up"
        invited_users.append({
            "email": invite.recipient,
            "description": description,
            "description_class": description_class,
        })
        invited_emails.add(invite.recipient)
    
    return render(request, "welcome.html", {
        "signup": signup,
        "referral_url": signup.referral_url(),
        "tweet_url": "https://twitter.com/share?{0}".format(urlencode({
            "url": signup.referral_url(),
            "text": REFERRAL_LINK_TEXT,
        })),
        "facebook_link_caption": REFERRAL_LINK_TEXT,
        "emailed": "emailed" in request.GET,
        "reward_tiers": reward_tiers,
        "max_reward_tier_signups": max_reward_tier_signups,
        "invited_users": invited_users,
    })

@require_POST
def share_email(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    
    fields = [{"Key": k, "Value": v} for k, v in {
        "inviter_referral_url": signup.referral_url(),
        "inviter_email": signup.email,
    }.iteritems()]
    subscribers = []
    
    for x in request.POST["emails"].split(","):
        addr = x.strip().lower()
        try:
            existing_signup = Signup.objects.get(email=addr)
            # If there's an existing signup, skip the invite
            continue
        except Signup.DoesNotExist:
            # Pass, so we invite the user.
            pass
        try:
            Invite(sender=signup, recipient=addr).save()
        except (ValidationError, IntegrityError):
            continue
        subscribers.append({
            "EmailAddress": addr,
            "Name": "Unknown",
            "CustomFields": fields,
        })
    
    try:
        if len(subscribers) > 0:
            Subscriber().import_subscribers(settings.CREATESEND_INVITEES_LIST_ID, subscribers, True, queue_subscription_based_autoresponders=True)
    except Exception:
        logging.exception("Exception importing invites to list")
    
    return HttpResponseRedirect("{0}?{1}".format(reverse(welcome, args=[signup.id]), urlencode({"emailed": "true"})))

def about(request):
    return render(request, "coming_soon.html")

def privacy(request):
    return render(request, "coming_soon.html")

def jobs(request):
    return render(request, "coming_soon.html")

def wreath(request):
    return render(request, "launchrock.html")

def refer(request, referral_key):
    request.session["referral_key"] = referral_key
    return redirect(home)

def advertisement_landing(request, advertisement_id):
    request.session["advertisement_id"] = advertisement_id
    return redirect(home)
