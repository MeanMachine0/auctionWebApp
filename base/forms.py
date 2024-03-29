from django import forms
import base.validators as validators

class ItemForm(forms.Form):
    name = forms.CharField(label="Item name", max_length=40)
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
    endDateTime = forms.DateTimeField(label="End date and time", validators=[validators.future])
    acceptReturns = forms.BooleanField(label="Accept returns", required=False)
    description = forms.CharField(widget=forms.Textarea, label="Description", max_length=1000)
    categories = [
        ("bOIS", "Business, Office & Industrial Supplies"),
        ("hB", "Health & Beauty"),
        ("f", "Fashion"),
        ("e", "Electronics"),
        ("hG", "Home Garden"),
        ("sHL", "Sports, Hobbies & Leisure"),
        ("mt", "Motors"),
        ("cA", "Collectables & Art"),
        ("mda", "Media"),
        ("o", "Other"),
    ]
    category = forms.ChoiceField(choices=categories, label="Category", widget=forms.Select(attrs={"style": "background-color: lightblue"}))

class BrowseForm(forms.Form):
    sortByChoices = [
        ("price", "Price"),
        ("numBids", "Bids"),
        ("name", "Name"),
        ("endDateTime", "End"),
    ]
    showNItemsChoices = [
        (10, "10"),
        (20, "20"),
        (50, "50"),
        (100, "100"),
    ]
    categoriesWithAll = ItemForm.categories
    categoriesWithAll.insert(0, ("all", "All"))
    conditions = ("new", "excellent", "good", "used", "refurbished", "partsOnly")
    search = forms.CharField(label="Search", required=False, widget=forms.TextInput(attrs={"style": "width: 155px;"}))
    category = forms.ChoiceField(choices=categoriesWithAll, label="Category", widget=forms.Select(attrs={"style": "background-color: lightblue;" "font-size: 20px;" "border: 2px solid black;" "max-width: 160px;"}))
    sortBy = forms.ChoiceField(choices=sortByChoices, label="Sort By", widget=forms.Select(attrs={"style": "background-color: lightblue;" "font-size: 20px;" "border: 2px solid black;"}))
    ascending = forms.BooleanField(label="Ascending", required=False, initial=True)
    lThan = forms.DecimalField(label="Price (£) ≥", decimal_places=2, initial=0, widget=forms.TextInput(attrs={"style": "width: 120px;"}))
    gThan = forms.DecimalField(label="Price (£) ≤", decimal_places=2, initial=9999999, widget=forms.TextInput(attrs={"style": "width: 120px;"}))
    new = forms.BooleanField(label="New", required=False, initial=True)
    excellent = forms.BooleanField(label="Excellent", required=False, initial=True)
    good = forms.BooleanField(label="Good", required=False, initial=True)
    used = forms.BooleanField(label="Used", required=False, initial=True)
    refurbished = forms.BooleanField(label="Refurbished", required=False, initial=True)
    partsOnly = forms.BooleanField(label="Parts Only", required=False, initial=True)
    areReturnsAccepted = forms.BooleanField(label="Returns Accepted", required=False, initial=True)
    areReturnsNotAccepted = forms.BooleanField(label="Returns Not Accepted", required=False, initial=True)
    showNItems = forms.ChoiceField(choices=showNItemsChoices, label="Max Results/Page", initial=20, widget=forms.Select(attrs={"style": "background-color: lightblue;" "font-size: 20px;" "border: 2px solid black;" "max-width: 160px;"}))

class BidForm(forms.Form):
    bid = forms.DecimalField(label="Bid (£)", decimal_places=2, max_digits=10)