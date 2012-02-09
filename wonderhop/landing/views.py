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

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for x in range(size))

def home(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email == "":
            context["error"] = "We need your email to reserve your spot!"
        else:
            try:
                signup = Signup.objects.get(email=email)
            except Signup.DoesNotExist:
                signup = Signup(email=email, referring_user=None)
                try:
                    signup.clean_fields(exclude=["referral_key"])
                except ValidationError as v:
                    #context["error"] = "Invalid email address"
                    raise
                else:
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

    return render(request, "signup.html", context)

def welcome(request, signup_id):
    signup = get_object_or_404(Signup, id=signup_id)
    return render(request, "welcome.html", {
        "signup": signup,
        "referral_url": request.build_absolute_uri(reverse(refer, args=[signup.referral_key])),
    })

def about(request):
    return render(request, "coming_soon.html")

def privacy(request):
    return render(request, "coming_soon.html")

def jobs(request):
    return render(request, "coming_soon.html")

def refer(request, referral_key):
    return redirect(home)
