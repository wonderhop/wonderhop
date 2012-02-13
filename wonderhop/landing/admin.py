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
def num_invites_sent(signup):
    return signup.sent_invites_set.count()
num_invites_sent.short_description = "Invites Sent"
class SignupAdmin(admin.ModelAdmin):
    inlines = [
        InviteInline,
    ]
    list_display = ("email", "sign_up_date", "referring_user", num_invites_sent)
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
