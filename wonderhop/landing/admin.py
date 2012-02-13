from django.contrib import admin
from wonderhop.landing.models import (
    Signup,
    IncentivePlan,
    IncentivePlanRewardTier,
    LandingSettings,
)

class SignupAdmin(admin.ModelAdmin):
    readonly_fields = ("sign_up_date",)
admin.site.register(Signup, SignupAdmin)

class IncentivePlanRewardTierInline(admin.TabularInline):
    model = IncentivePlanRewardTier
class IncentivePlanAdmin(admin.ModelAdmin):
    inlines = [
        IncentivePlanRewardTierInline,
    ]
admin.site.register(IncentivePlan, IncentivePlanAdmin)

class LandingSettingsAdmin(admin.ModelAdmin):
    exclude = ("id",)
admin.site.register(LandingSettings, LandingSettingsAdmin)
