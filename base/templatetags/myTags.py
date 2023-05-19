from django import template
from base.models import Account

register = template.Library()

@register.simple_tag
def idToUsername(id):
    return Account.objects.get(pk=id).user.username

@register.simple_tag
def numToMoney(dec):
    dec = str(dec)
    if '.' in dec:
        b1, b2 = dec.split('.')
        if len(b2) == 1:
            b2 = f"{b2}0"
        lb1 = len(b1)
        if lb1 >= 4:
            first = True
            indices = []
            while lb1 >= 3:
                lb1 = lb1 - 4 if first else lb1 - 3
                indices.append(lb1)
                first = False
            for index in indices:
                b1 = f"{b1[:index]}{b1[index]},{b1[index+1:]}"
        money = '.'.join([b1, b2])   
    else:
        money = f"{dec}.00"  
    return (money)
    