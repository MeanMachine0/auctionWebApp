import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
import django
django.setup()
from django.core.management.base import BaseCommand
import schedule
from django.utils import timezone
from hello.models import ListItem, LogItem

def countLogItems():
    print(str(LogItem.objects.all().count()) + " items sold.\n")

def transferItems():
    soldItems = ListItem.objects.filter(endDateTime__lte=timezone.now())
    numSoldItems = soldItems.count()

    if numSoldItems > 0:
        singPlural = " items" if numSoldItems > 1 else " item"
        print("Transferring " + str(numSoldItems) + singPlural + "...")
        for item in soldItems:
            LogItem.objects.create(name=item.name, soldDateTime=item.endDateTime)
        soldItems.delete()
        print(str(numSoldItems) + singPlural + " transferred.")
    
    else:
        print("No items to transfer.")

    countLogItems()

class Command(BaseCommand):
    help = "Runs transferItems every 10 seconds."

    def handle(self, *args, **options):
        schedule.every(10).seconds.do(transferItems)

        while True:
            schedule.run_pending()