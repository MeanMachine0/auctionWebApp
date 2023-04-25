import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webProject.settings')
import django
django.setup()
from django.core.management.base import BaseCommand
import schedule
from django.utils import timezone
from base.models import Account, Item
from django.db.models import Q

def updateItems():
    notUpdatedEndedItems = Item.objects.filter(Q(endDateTime__lte=timezone.now()) & Q(ended=False))
    notUpdatedSoldItems = notUpdatedEndedItems.filter(numBids__gte=1)
    numNotUpdatedEndedItems = notUpdatedEndedItems.count()
    if numNotUpdatedEndedItems > 0:
        singPlural = " items" if numNotUpdatedEndedItems > 1 else " item"
        print("Updating " + str(numNotUpdatedEndedItems) + singPlural + "...")
        for item in notUpdatedSoldItems:
            transaction = True
            while transaction is True:
                price = item.price
                buyer = Account.objects.get(pk=item.buyer_id)
                seller = Account.objects.get(pk=item.seller_id)
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

            item.ended=True
            if transaction is True: 
                item.destinationAddress=buyer.address
                item.sold=True
                item.transactionSuccess=True
            else:
                item.transactionSuccess=False
            item.save()

        for item in notUpdatedEndedItems:
            if item not in notUpdatedSoldItems:
                item.ended=True
                item.save()
        print(str(numNotUpdatedEndedItems) + singPlural + " updated.")

    else:
        print("No items to update.")

class Command(BaseCommand):
    help = "Runs updateItems every 5 seconds."

    def handle(self, *args, **options):
        schedule.every(5).seconds.do(updateItems)

        while True:
            schedule.run_pending()