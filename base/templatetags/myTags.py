from django import template
from base.models import Account

register = template.Library()

@register.simple_tag
def idToUsername(id):
    return Account.objects.get(pk=id).user.username