from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import OAuthLoginAttempt, SocialIdentity, User


@admin.register(User)
class UniWayUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("UniWay", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("UniWay", {"fields": ("email", "role")}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(SocialIdentity)
class SocialIdentityAdmin(admin.ModelAdmin):
    list_display = ("provider", "user", "email_at_link", "created_at", "last_login_at")
    list_filter = ("provider",)
    search_fields = ("user__email", "email_at_link", "subject")
    readonly_fields = ("provider", "user", "subject", "email_at_link", "created_at", "last_login_at")


@admin.register(OAuthLoginAttempt)
class OAuthLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("created_at", "expires_at", "consumed_at")
    readonly_fields = ("state_digest", "nonce_digest", "created_at", "expires_at", "consumed_at")
