import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
import django
django.setup()
from django.core.management.base import BaseCommand
import schedule
from django.utils import timezone
from hello.models import Accounts, Items, EndedItems
from django.db.models import Q

def transferItems():
    endedItems = Items.objects.filter(endDateTime__lte=timezone.now())
    soldItems = endedItems.filter(numBids__gte=1)    
    numEndedItems = endedItems.count()

    if endedItems.count() > 0:
        singPlural = " items" if numEndedItems > 1 else " item"
        print("Transferring " + str(numEndedItems) + singPlural + "...")
        for item in soldItems:
            transaction = True
            while transaction is True:
                price = item.price
                buyer = Accounts.objects.all().get(user__username=item.buyerId)
                seller = Accounts.objects.all().get(user__username=item.sellerId)
                #Attempting buyer side of transaction:
                try:
                    buyer.balance -= price
                    buyer.save()
                #If the buyer's balance fails to save, the transaction quits:
                except:
                    transaction = False
                
                #Attempting seller side of transaction:
                try:
                    seller.balance += price
                    seller.save()
                    break
                #If the seller's balance fails to save, the buyer's balance is returned to its value before the transaction began.
                except:
                    buyer.balance += price
                    buyer.save()
                    transaction = False

                if transaction is True: 
                    item.sold = True
                    item.save()
                    
        for item in endedItems:
            EndedItems.objects.create(name=item.name, salePrice=item.price, postageCost=item.postageCost, bidIncrement=item.bidIncrement, 
                                        condition=item.condition, endDateTime=item.endDateTime, acceptReturns=item.acceptReturns,
                                        description=item.description, numBids=item.numBids, sold=item.sold, buyerId=item.buyerId, sellerId=item.sellerId)
        endedItems.delete()
        print(str(numEndedItems) + singPlural + " transferred.")

    else:
        print("No items to transfer.")

class Command(BaseCommand):
    help = "Runs transferItems every 5 seconds."

    def handle(self, *args, **options):
        schedule.every(5).seconds.do(transferItems)

        while True:
            schedule.run_pending()