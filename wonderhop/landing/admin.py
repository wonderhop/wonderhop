from django.contrib import admin
from wonderhop.landing.models import Signup

class SignupAdmin(admin.ModelAdmin):
    readonly_fields = ("sign_up_date",)

admin.site.register(Signup, SignupAdmin)

