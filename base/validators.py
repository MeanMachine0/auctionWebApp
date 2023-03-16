from django.core.exceptions import ValidationError
from django.utils import timezone

def future(dateTime):
    if dateTime <= timezone.now():
        raise ValidationError("The end date and time must be set to a future date/time.")