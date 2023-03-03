from django.db import models
from django import forms
from django.utils import timezone

class LogItem(models.Model):
    name = models.CharField(max_length=40)
    soldDateTime = models.DateTimeField("Date/Time Logged")

    def __str__(self):
        date = timezone.localtime(self.soldDateTime)
        return f"'{self.name}' sold at {date.strftime('%A, %d %B, %Y at %X')}"

class LogMessage(models.Model):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        date = timezone.localtime(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"

class ListItem(models.Model):
    name = models.CharField(max_length=40)
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

    def __str__(self):
        return self.name