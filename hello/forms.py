from django import forms
from hello.models import LogMessage
from hello.models import ListItem

class LogMessageForm(forms.ModelForm):
    class Meta:
        model = LogMessage
        fields = ("message",)   # NOTE: the trailing comma is required

class ListItemForm(forms.Form):
    name = forms.CharField(label="Item name")
    price = forms.DecimalField(label="Starting price (£)", decimal_places=2)
    postageCost = forms.DecimalField(label="Postage cost (£)", decimal_places=2)
    bidIncrement = forms.DecimalField(label="Bid increment (£)", decimal_places=2)
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

class BrowseForm(forms.Form):
    sortByChoices = [
        ("id", "Id"),
        ("name", "Name"),
        ("price", "Price"),
        ("endDateTime", "Time Remaining"),
    ]
    conditions = ("new", "excellent", "good", "used", "refurbished", "partsOnly")
    
    search = forms.CharField(label="Search", required=False, widget=forms.TextInput(attrs={"style": "width: 155px;"}))
    sortBy = forms.ChoiceField(choices=sortByChoices, label="Sort By", widget=forms.Select(attrs={"style": "background-color: lightblue;" "font-size: 20px;" "border: 2px solid black;"}))
    ascending = forms.BooleanField(label="Ascending", required=False, initial=True)
    lThan = forms.DecimalField(label="Price (£) ≥", decimal_places=2, initial=0, widget=forms.TextInput(attrs={"style": "width: 120px;"}))
    gThan = forms.DecimalField(label="Price (£) ≤", decimal_places=2, initial=9999999999, widget=forms.TextInput(attrs={"style": "width: 120px;"}))
    new = forms.BooleanField(label="New", required=False, initial=True)
    excellent = forms.BooleanField(label="Excellent", required=False, initial=True)
    good = forms.BooleanField(label="Good", required=False, initial=True)
    used = forms.BooleanField(label="Used", required=False, initial=True)
    refurbished = forms.BooleanField(label="Refurbished", required=False, initial=True)
    partsOnly = forms.BooleanField(label="Parts Only", required=False, initial=True)
    areReturnsAccepted = forms.BooleanField(label="Returns Accepted", required=False, initial=True)
    areReturnsNotAccepted = forms.BooleanField(label="Returns Not Accepted", required=False, initial=True)