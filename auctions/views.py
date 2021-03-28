from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django import forms
from django.contrib import messages

from .models import User, Listing, Category, Watchlist, Bid, Comment


class ListingForm(ModelForm):
    class Meta:
        model = Listing 
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'custom-file-input'}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bidding']
        widgets = {
            'bidding': forms.NumberInput(attrs={'class': 'form-control'})
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.TextInput(attrs={'class': 'form-control'})
        }


def index(request):
    listings = Listing.objects.filter(status=1)
    if request.user.is_authenticated:
        watched_items = len(Watchlist.objects.filter(user=request.user, item__status=1))
    else:
        watched_items = 0

    return render(request, "auctions/index.html", {
        "listings": listings,
        "watched_items": watched_items
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    watched_items = len(Watchlist.objects.filter(user=request.user, item__status=1))
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            form.clean()
            Listing = form.save(commit=False)
            Listing.user = request.user
            # TODO: Slug generieren
            Listing = Listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form,
                "watched_items": watched_items
            })
    else:
        return render(request, "auctions/create_listing.html", {
            "form": ListingForm(),
            "watched_items": watched_items
        })


def view_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing=listing)
    bids = Bid.objects.filter(listing=listing)
    highest_bid = bids.aggregate(Max('bidding'))
    you_won = False
    highest_bidder = False

    if request.user.is_authenticated:
        watchlist = Watchlist.objects.filter(user=request.user, item__title=listing.title)
        watched_items = len(Watchlist.objects.filter(user=request.user, item__status=1))
    else:
        watchlist = None
        watched_items = 0

    # Search for highest bidder and confirm as winner if auction is closed
    if highest_bid["bidding__max"]:
        prelim_winner = bids.get(bidding=int(highest_bid['bidding__max']))
        if listing.status == False:
            winner = prelim_winner.user
            if request.user == winner:
                you_won = True
        elif request.user == prelim_winner.user:
            highest_bidder = True

    created_by_current_user = (request.user == listing.user) # Determine signed in user
    watch_btn = not watchlist # Determine whether listing is already on watchlist

    if request.method == "POST":
        bid_form = BidForm(request.POST)
        comment_form = CommentForm(request.POST)

        context = {
            "listing": listing,
            "bid_form": bid_form,
            "no_bids": len(bids),
            "highest_bid": highest_bid,
            "highest_bidder": highest_bidder,
            "you_won": you_won,
            "comment_form": comment_form,
            "comments": comments,
            "watch_btn": watch_btn,
            "watched_items": watched_items
        }

        if 'bidding' in request.POST:
            if bid_form.is_valid():
                bidding = bid_form.cleaned_data["bidding"]
                if (bids and bidding > int(highest_bid['bidding__max'])) or (not bids and bidding >= listing.starting_bid):
                    new_bidding = Bid(user=request.user, listing=listing, bidding=bidding)
                    new_bidding.save()
                    messages.success(request, 'Your bid was successful!')
                else:
                    messages.error(request, 'Error! Your bid is too low.')
                return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
            else:
                return render(request, "auctions/view_listing.html", context)
        elif 'close' in request.POST:
            listing.status = False
            listing.save()
            if highest_bid['bidding__max']:
                prelim_winner.status = True
                prelim_winner.save()
            return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
        elif 'comment' in request.POST:
            if comment_form.is_valid():
                comment = comment_form.cleaned_data["comment"]
                new_comment = Comment(listing=listing, comment=comment)
                new_comment.save()
                return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
            else:
                return render(request, "auctions/view_listing.html", context)
        elif 'watch' in request.POST:
            if not watchlist:
                watch_listing = Watchlist(user=request.user)
                watch_listing.save()
                watch_listing.item.add(listing)
            else:
                watchlist.delete()
            return HttpResponseRedirect(reverse("view_listing", args=(listing_id,)))
    
    else:
        return render(request, "auctions/view_listing.html", {
            "listing": listing,
            "bid_form": BidForm(),
            "no_bids": len(bids),
            "highest_bid": highest_bid,
            "highest_bidder": highest_bidder,
            "you_won": you_won,
            "comment_form": CommentForm(),
            "comments": comments,
            "created_by_current_user": created_by_current_user,
            "watch_btn": watch_btn,
            "watched_items": watched_items
        })


@login_required
def watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)
    watched_items = len(Watchlist.objects.filter(user=request.user, item__status=1))
    watched_listings = []
    for item in watchlist:
        watched = item.item.all()
        for listing in watched:
            watched_listings.append(listing.title)
    listings = Listing.objects.filter(title__in=watched_listings)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watched_listings,
        "listings": listings,
        "watched_items": watched_items
    })


def categories(request):
    categories = Category.objects.all()
    if request.user.is_authenticated:
        watched_items = len(Watchlist.objects.filter(user=request.user, item__status=1))
    else:
        watched_items = 0
    
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "watched_items": watched_items
    })


def category(request, category):
    category_id = Category.objects.get(category=category)
    listings = Listing.objects.filter(status=1, category=category_id)
    if request.user.is_authenticated:
        watched_items = len(Watchlist.objects.filter(user=request.user, item__status=1))
    else:
        watched_items = 0

    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings,
        "watched_items": watched_items
    })


def history(request):
    listings = Listing.objects.filter(status=0)
    return render(request, "auctions/history.html", {
        "listings": listings
    })