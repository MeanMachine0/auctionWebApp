from django.contrib import admin
from .models import Accounts, Items, EndedItems

admin.site.register(Accounts)
admin.site.register(Items)
admin.site.register(EndedItems)