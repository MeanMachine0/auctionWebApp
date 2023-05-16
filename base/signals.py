from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from base.models import Account, Item
from random import randint
import firebase_admin
from firebase_admin import credentials, messaging
import os

names=["King's", "Queen's", "Rook's", "Bishop's", "Knight's", "Pawn's"]
streetNames=["Street", "Road", "Lane", "Avenue", "Boulevard", "Drive", "Court", "Way"]

def randAddress():
    return str(randint(1, 99)) + " " + names[randint(0, len(names)-1)] + " " + streetNames[randint(0, len(streetNames)-1)]

@receiver(post_save, sender=User)
def onNewUser(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance, address=randAddress())

@receiver(pre_save, sender=Item)
def onItemSaved(sender, instance, **kwargs):
    try:
        previousInstance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if previousInstance.buyer != None:
        if previousInstance.buyer != instance.buyer and previousInstance.buyer.fcmToken != None:
            message = messaging.Message(
                notification=messaging.Notification(
                title="Outbidded!",
                body=f"On: {instance.name}.",
                ),
                data={'itemId': f'{instance.id}'},
                token=previousInstance.buyer.fcmToken,
            )
            messaging.send(message)
