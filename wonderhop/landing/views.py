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
                params = { "referral_link": _referral_url(request, signup)}
                m = EmailMultiAlternatives(
                    subject="Thank you for signing up for WonderHop!",
                    body=render_to_string("welcome_email.txt", params),
                    from_email="WonderHop <contact@wonderhop.com>",
                    to=[signup.email]
                )
                m.attach_alternative(render_to_string("welcome_email.html", params), "text/html")
                m.send(fail_silently=True)
                
                if referring_user is not None:
                    new_reward = None
                    if referring_user.incentive_plan is not None:
                        new_rewards = list(referring_user.incentive_plan.reward_tiers.filter(num_signups=referring_user.referred_user_set.count()))
                        if len(new_rewards) > 0:
                            # There should only be one, presumably
                            new_reward = new_rewards[0]
                    
                    params = {
                        "referral_link": _referral_url(request, referring_user),
                        "new_reward": new_reward,
                    }
                    m = EmailMultiAlternatives(
                        subject="Someone you invited signed up for WonderHop",
                        body=render_to_string("invite_accepted_email.txt", params),
                        from_email="WonderHop <contact@wonderhop.com>", 
                        to=[referring_user.email],
                    )
                    m.attach_alternative(render_to_string("invite_accepted_email.html", params), "text/html")
                    m.send(fail_silently=True)
                
            return redirect(welcome, signup.id)
        except ValidationError as v:
            context["error"] = "Invalid email address"
    
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

def welcome(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    REFERRAL_LINK_TEXT = "Join me on WonderHop for up to 60% off unique decor, kitchen treats, and family finds to make life one-of-a-kind."
    
    if signup.incentive_plan is None:
        reward_tiers = []
    else:
        reward_tiers = signup.incentive_plan.reward_tiers.order_by("num_signups").all()
    
    return render(request, "welcome.html", {
        "signup": signup,
        "referral_url": _referral_url(request, signup),
        "tweet_url": "https://twitter.com/share?{0}".format(urlencode({
            "url": _referral_url(request, signup),
            "text": REFERRAL_LINK_TEXT,
        })),
        "facebook_link_caption": REFERRAL_LINK_TEXT,
        "emailed": "emailed" in request.GET,
        "reward_tiers": reward_tiers,
    })

@require_POST
def share_email(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    
    def invite_email(to_addr):
        params = {
            "url": _referral_url(request, signup),
        }
        m = EmailMultiAlternatives(
                subject="You've been invited to join WonderHop!",
                body=render_to_string("invite_email.txt", params),
                from_email="WonderHop <contact@wonderhop.com>", 
                to=[to_addr],
            )
        m.attach_alternative(render_to_string("invite_email.html", params), "text/html")
        return m
    
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
