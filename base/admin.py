from django.contrib import admin
from .models import Account, Item, Movie

admin.site.register(Account)
admin.site.register(Item)
admin.site.register(Movie)