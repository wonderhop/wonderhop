from django.contrib import admin
from wonderhop.landing.models import (
    Signup,
    Invite,
    IncentivePlan,
    IncentivePlanRewardTier,
    LandingSettings,
)

class InviteInline(admin.TabularInline):
    model = Invite
    readonly_fields = ("recipient", "sent_date",)
    extra = 0
class SignupAdmin(admin.ModelAdmin):
    inlines = [
        InviteInline,
    ]
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
