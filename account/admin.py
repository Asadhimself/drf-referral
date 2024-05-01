from django.contrib import admin

from .models import Account, InviteKey, PhoneToken


admin.site.register(Account)
admin.site.register(InviteKey)
admin.site.register(PhoneToken)
