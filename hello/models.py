from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import CheckConstraint, Q
import json

class Accounts(models.Model): 
    user=models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    address=models.CharField(max_length=40)
    balance=models.DecimalField(decimal_places=2, max_digits=10, default=0, validators=[MinValueValidator(0)])

    class Meta:
        constraints = (
            CheckConstraint(
                check=Q(balance__gte=0), 
                name="minBalance"),
            )

    def __str__(self):
        return str(self.id)
    
class Items(models.Model): 
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    postageCost = models.DecimalField(decimal_places=2, max_digits=10)
    bidIncrement = models.DecimalField(decimal_places=2, max_digits=10)
    conditionChoices = [
        ("new", "New"),
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("used", "Used"),
        ("refurbished", "Refurbished"),
        ("partsOnly", "Parts Only"),
    ]
    condition = models.CharField(max_length=20, choices=conditionChoices)
    endDateTime = models.DateTimeField()
    acceptReturns = models.BooleanField(default=False)
    description = models.TextField(max_length=1000)
    numBids = models.IntegerField(default=0)
    bidders = models.CharField(max_length=999999999, default='[]')
    sold = models.BooleanField(default=False)
    buyerId = models.ForeignKey(Accounts, to_field="id", on_delete=models.DO_NOTHING, related_name="bId", blank=True, null=True)
    sellerId = models.ForeignKey(Accounts, to_field="id", on_delete=models.DO_NOTHING, related_name="sId", blank=True, null=True)

    def getBidders(self):
        return json.loads(self.bidders)
    
    def setBidders(self, value):
        self.bidders = json.dumps(value)

    biddersProperty = property(getBidders, setBidders)

    def __str__(self):
        return self.name
    
class EndedItems(models.Model):
    name = models.CharField(max_length=50)
    salePrice = models.DecimalField(decimal_places=2, max_digits=10)
    postageCost = models.DecimalField(decimal_places=2, max_digits=10)
    bidIncrement = models.DecimalField(decimal_places=2, max_digits=10)
    conditionChoices = [
        ("new", "New"),
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("used", "Used"),
        ("refurbished", "Refurbished"),
        ("partsOnly", "Parts Only"),
    ]
    condition = models.CharField(max_length=20, choices=conditionChoices)
    endDateTime = models.DateTimeField("Date/Time Logged")
    acceptReturns = models.BooleanField()
    description = models.TextField(max_length=1000)
    numBids = models.IntegerField()
    bidders = models.CharField(max_length=999999999, default='[]')
    sold = models.BooleanField()
    buyerId = models.IntegerField(blank=True, null=True)
    sellerId = models.IntegerField()
    destinationAddress = models.CharField(max_length=40, blank=True, null=True)

    def getBidders(self):
        return json.loads(self.bidders)
    
    def setBidders(self, value):
        self.bidders = json.dumps(value)

    biddersProperty = property(getBidders, setBidders)

    def __str__(self):
        date = timezone.localtime(self.endDateTime)
        return f"'{self.name}' ended at {date.strftime('%A, %d %B, %Y at %X')}"

class LogMessage(models.Model):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        date = timezone.localtime(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"