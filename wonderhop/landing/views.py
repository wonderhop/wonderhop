from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from wonderhop.landing.forms import SignupForm

def home(request):
    form = SignupForm(request.POST or None)
    context = {"form": form}

    if form.is_valid():
        form.save()
        return redirect("thanks")
    elif form.is_bound:
        context["error"] = "You need to give us an email so we can contact you!"

    return render_to_response("signup.html", context, RequestContext(request))

def thanks(request):
    return render_to_response("thanks.html", {}, RequestContext(request))
