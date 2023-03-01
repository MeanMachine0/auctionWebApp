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
    condition = forms.ChoiceField(choices=conditionChoices, label="Condition", widget=forms.Select(attrs={"style": "background-color: lightblue"}))
    endDateTime = forms.DateTimeField(label="End date and time")
    acceptReturns = forms.BooleanField(label="Accept returns", required=False)
    description = forms.CharField(widget=forms.Textarea, label="Description")

class SortAndFilterByForm(forms.Form):
    sortByChoices = [
        ("id", "Id"),
        ("name", "Name"),
        ("price", "Price"),
        ("endDateTime", "Time Remaining"),
    ]
    conditionChoices = [
        ("new", "New"),
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("used", "Used"),
        ("refurbished", "Refurbished"),
        ("partsOnly", "Parts Only"),
    ]
    sortBy = forms.ChoiceField(choices=sortByChoices, label="Sort By", widget=forms.Select(attrs={"style": "background-color: lightblue;" "font-size: 20px;" "border: 2px solid black;"}))
    ascending = forms.BooleanField(label="Ascending", required=False, initial=True)
    lThan = forms.DecimalField(label="Price >", decimal_places=2, initial=0)
    gThan = forms.DecimalField(label="Price <", decimal_places=2, initial=99999999)
    isNew = forms.BooleanField(label=conditionChoices[0][1], required=False, initial=True)
    isExcellent = forms.BooleanField(label=conditionChoices[1][1], required=False, initial=True)
    isGood = forms.BooleanField(label=conditionChoices[2][1], required=False, initial=True)
    isUsed = forms.BooleanField(label=conditionChoices[3][1], required=False, initial=True)
    isRefurbished = forms.BooleanField(label=conditionChoices[4][1], required=False, initial=True)
    isPartsOnly = forms.BooleanField(label=conditionChoices[5][1], required=False, initial=True)
    areReturnsAccepted = forms.BooleanField(label="Returns Accepted", required=False, initial=True)
    areReturnsNotAccepted = forms.BooleanField(label="Returns Not Accepted", required=False, initial=True)