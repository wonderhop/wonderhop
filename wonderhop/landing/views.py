from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from wonderhop.landing.models import Signup
import random
import string
from urllib import urlencode

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
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
                signup = Signup(email=email, referring_user=referring_user)
                # Validate the email field, raise ValidationError if it fails
                signup.clean_fields(exclude=["referral_key"])
                MAX_ATTEMPTS = 5
                for attempt in xrange(MAX_ATTEMPTS):
                    try:
                        signup.referral_key = id_generator()
                        signup.save()
                    except IntegrityError:
                        if attempt == MAX_ATTEMPTS - 1:
                            raise
                    else:
                        break
            return redirect(welcome, signup.id)
        except ValidationError as v:
            context["error"] = "Invalid email address"
    
    return render(request, "signup.html", context)

def welcome(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    referral_url = request.build_absolute_uri(reverse(refer, args=[signup.referral_key]))
    REFERRAL_LINK_TEXT = "Join me on WonderHop for up to 60% off unique decor, kitchen treats, and family finds to make life one-of-a-kind."
    
    return render(request, "welcome.html", {
        "signup": signup,
        "referral_url": referral_url,
        "tweet_url": "https://twitter.com/share?{0}".format(urlencode({
            "url": referral_url,
            "text": REFERRAL_LINK_TEXT,
        })),
        "facebook_link_caption": REFERRAL_LINK_TEXT,
    })

def about(request):
    return render(request, "coming_soon.html")

def privacy(request):
    return render(request, "coming_soon.html")

def jobs(request):
    return render(request, "coming_soon.html")

def refer(request, referral_key):
    request.session["referral_key"] = referral_key
    return redirect(home)
