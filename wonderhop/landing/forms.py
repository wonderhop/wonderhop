from django.forms import (
    ModelForm, 
)
from wonderhop.landing.models import Signup


class SignupForm(ModelForm):
    class Meta:
        model = Signup
