from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.core.mail import (
    send_mail,
    EmailMessage,
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
from urllib import urlencode

def _id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))

def _referral_url(request, signup):
    return request.build_absolute_uri(reverse(refer, args=[signup.referral_key]))

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
                signup = Signup(email=email, referring_user=referring_user)
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
                # TODO this should be a signal on Signup
                send_mail(
                    "Thank you for signing up for WonderHop!",
                    render_to_string("welcome_email.txt", { "referral_link": _referral_url(request, signup)}),
                    "WonderHop <contact@wonderhop.com>", [signup.email], fail_silently=True,
                )
                
                if referring_user is not None:
                    new_reward = None
                    if referring_user.incentive_plan is not None:
                        new_rewards = list(referring_user.incentive_plan.reward_tiers.filter(num_signups=referring_user.referred_user_set.count()))
                        if len(new_rewards) > 0:
                            # There should only be one, presumably
                            new_reward = new_rewards[0]
                    
                    send_mail(
                        "Someone you invited signed up for WonderHop",
                        render_to_string("invite_accepted_email.txt", {
                            "referral_link": _referral_url(request, referring_user),
                            "new_reward": new_reward,
                        }),
                        "WonderHop <contact@wonderhop.com>", [referring_user.email], fail_silently=True,
                    )
                
            return redirect(welcome, signup.id)
        except ValidationError as v:
            context["error"] = "Invalid email address"
    
    return render(request, "signup.html", context)

def welcome(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    REFERRAL_LINK_TEXT = "Join me on WonderHop for up to 60% off unique decor, kitchen treats, and family finds to make life one-of-a-kind."
    
    return render(request, "welcome.html", {
        "signup": signup,
        "referral_url": _referral_url(request, signup),
        "tweet_url": "https://twitter.com/share?{0}".format(urlencode({
            "url": _referral_url(request, signup),
            "text": REFERRAL_LINK_TEXT,
        })),
        "facebook_link_caption": REFERRAL_LINK_TEXT,
        "emailed": "emailed" in request.GET,
    })

@require_POST
def share_email(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    
    def invite_email(to_addr):
        return EmailMessage(
                subject="You've been invited to join WonderHop!",
                body="""One of your friends has invited you to join WonderHop, where you get up to 60% off unique decor, kitchen treats, and family finds to make life one-of-a-kind.

Just use this link to sign up and give credit to the person who invited you:
{url}""".format(url=_referral_url(request, signup)),
                from_email="WonderHop <contact@wonderhop.com>", 
                to=[to_addr],
            )
    
    messages = []
    for x in request.POST["emails"].split(","):
        addr = x.strip().lower()
        try:
            Invite(sender=signup, recipient=addr).save()
        except (ValidationError, IntegrityError):
            continue
        messages.append(invite_email(addr))
    
    get_connection().send_messages(messages)
    return HttpResponseRedirect("{0}?{1}".format(reverse(welcome, args=[signup.id]), urlencode({"emailed": "true"})))

def about(request):
    return render(request, "coming_soon.html")

def privacy(request):
    return render(request, "coming_soon.html")

def jobs(request):
    return render(request, "coming_soon.html")

def refer(request, referral_key):
    request.session["referral_key"] = referral_key
    return redirect(home)
