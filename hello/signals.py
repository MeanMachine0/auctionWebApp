from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from hello.models import Accounts
from random import randint

names=["King's", "Queen's", "Rook's", "Bishop's", "Knight's", "Pawn's"]
streetNames=["Street", "Road", "Lane", "Avenue", "Boulevard", "Drive", "Court", "Way"]

def randAddress():
    return names[randint(0, len(names)-1)] + " " + streetNames[randint(0, len(streetNames)-1)]

@receiver(post_save, sender=User)
def onNewUser(sender, instance, created, **kwargs):
    if created:
        Accounts.objects.create(user=instance, address=randAddress())