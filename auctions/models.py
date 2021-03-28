from django.contrib.auth.models import AbstractUser
from django.db import models
from commerce import settings
from django.utils import timezone
from django.db.models import Max

class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"


class Listing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.TextField(default="")
    starting_bid = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images', default="No image provided")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)
    status = models.BooleanField(default=1)
    date = models.DateTimeField(default=timezone.now)
    # slug = models.TextField(unique, slugify, wenn Titel bereits vergeben, Zahl anhängen, in Funktion auslagern)

    def __str__(self):
        return f"Listing {self.id}: {self.title}"
    
    def latest_price(self):
        bids = Bid.objects.filter(listing=self)
        highest_bid = bids.aggregate(Max('bidding'))
        if highest_bid["bidding__max"]:
            return highest_bid["bidding__max"]
        else:
            return self.starting_bid



class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ManyToManyField(Listing)

    def __str__(self):
        return f"Watchlist {self.user} - {self.item.all()}"


class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bidding = models.IntegerField()
    status = models.BooleanField(default=0)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Bid value: ${self.bidding}" 


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.TextField(default="")

    def __str__(self):
        return f"{self.comment} ({self.listing})"
