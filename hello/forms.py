from django import forms
from hello.models import LogMessage
from hello.models import ListItem

class LogMessageForm(forms.ModelForm):
    class Meta:
        model = LogMessage
        fields = ("message",)   # NOTE: the trailing comma is required

class ListItemForm(forms.Form):
    name = forms.CharField(label="Item name")
    price = forms.DecimalField(label="Starting price", decimal_places=2)
    postageCost = forms.DecimalField(label="Postage cost", decimal_places=2)
    bidIncrement = forms.DecimalField(label="Bid increment", decimal_places=2)
    conditionChoices = [
        ("new", "New"),
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("used", "Used"),
        ("refurbished", "Refurbished"),
        ("partsOnly", "Parts Only"),
    ]
    condition = forms.ChoiceField(choices=conditionChoices, label="Condition")
    endDateTime = forms.DateTimeField(label="End date and time")
    acceptReturns = forms.BooleanField(label="Accept returns", required=False)
    description = forms.CharField(widget=forms.Textarea, label="Description")

class SortByForm(forms.Form):
    sortByChoices = [
        ("id", "Id"),
        ("name", "Name"),
        ("price", "Price"),
        ("endDateTime", "Time Remaining"),
    ]
    sortBy = forms.ChoiceField(choices=sortByChoices, label="Sort By")
    ascending = forms.BooleanField(label="Ascending", required=False)