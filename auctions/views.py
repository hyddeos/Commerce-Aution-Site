from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listings, Bid, Comment, Watchlist


def index(request):    

    return render(request, "auctions/index.html", {
        "active_items": get_items_with_bid(),
        "inactive_items": get_inactive_items()
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
def new_auction(request):

    if request.method == "POST":
        category = request.POST["category"]
        title = request.POST["title"]
        description = request.POST["description"]
        image = request.POST["image"]
        starting_bid = request.POST["starting_bid"]
        
        user = request.user

        # Saves the request to database
        auction_object = Listings(category=category, title=title, description=description, image=image, creator=user)
        auction_object.save()
        bid = Bid(item=auction_object, bid=starting_bid, username=user)
        bid.save()

        return HttpResponseRedirect(reverse("index"))  

    return render(request, "auctions/new_auction.html", {
        "categorys": get_categorys(),
        "user": request.user
    })


def item(request, item_id):  

    user = request.user
    creator = Listings.objects.get(pk=item_id).creator
    bid = Bid.objects.get(item=item_id).bid
    bid_min = bid+1
    creator_status = False
    has_bids = True
    watchlist_status = False    
    winner = Bid.objects.get(item=item_id).username

    # Winner check. See if the user the winner   
    if winner == user:
        winner = "You"

    # Bid check, Has the items any bidders?
    if creator == Bid.objects.get(item=item_id).username:
        has_bids = False
        bid_min -= 1

    # Creator check
    if user == creator:
        creator_status = True

        if request.method == "POST":
            status = request.POST["auction_status"]

            # End Auction
            if status == "end_auction":
                end_auction = Listings.objects.get(pk=item_id)
                end_auction.active = False
                end_auction.save()
                return HttpResponseRedirect(reverse("index"))

    # On watchlist check
    watchlist_status = False 
    if user:
        watching = Watchlist.objects.filter(username=user, watch=item_id)
        if watching:
            watchlist_status = True

    if request.method == "POST":
        new_bid = request.POST["new_bid"]
        try:
            if int(new_bid) > bid:
                update_bid = Bid.objects.filter(item=item_id).update(bid=new_bid, username=user)
                update_bid.save()
                return HttpResponseRedirect(reverse("index"))
        except:
            return HttpResponseRedirect(reverse("index"))
        
    # Page rendering
    try:    
        return render(request, "auctions/item.html/", {
            "active": Listings.objects.get(pk=item_id).active,
            "item": Listings.objects.get(pk=item_id),
            "creator": creator_status,
            "watchlist": watchlist_status,
            "bid": bid,
            "bid_min": bid_min,
            "winner": winner,
            "comments": Comment.objects.filter(item=item_id)
        })
    # If item don´t exists, redirect to start-page
    except Listings.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))



@login_required
def watchlist(request):

    user = request.user
    watchlist_items = Watchlist.objects.filter(username=user)

    # User has 0 items in watchlist
    if len(watchlist_items) == 0:
       return render(request, "auctions/watchlist.html", {  
            "list": False,
        }) 
    # User has items in watchlist
    return render(request, "auctions/watchlist.html", {  
            "list": watchlist_items,
        })


@login_required
def watchlist_func(request, item_id):

    user = request.user
    watching = Watchlist.objects.filter(username=user, watch=item_id).exists()
    item = Listings.objects.get(pk=item_id)

    if watching:
        remove = Watchlist.objects.get(username=user, watch=item_id)
        remove.delete()
    else:
        add = Watchlist(username=user, watch=item)
        add.save()

    return HttpResponseRedirect(reverse("watchlist"))


@login_required
def comment(request, item_id):

    # Check if item exists
    if Listings.objects.filter(pk=item_id).exists():        

        if request.method == "POST":

            user = request.user
            get_comment = request.POST["get_comment"]
            comment = Comment(comment=get_comment, username=user, item=Listings.objects.get(pk=item_id))
            comment.save()    
            # Redirects back to the item after post    
            return HttpResponseRedirect('/item/' + str(item_id))
        
        return render(request, "auctions/comment.html/", {
            "title": Listings.objects.get(pk=item_id).title,
        })
    else:
        return HttpResponseRedirect(reverse("index"))


def category(request, *args, **kwargs):

    #"active_items": Listings.objects.filter(category=kwargs.get('category'), active=True),
    #       "inactive_items": Listings.objects.filter(category=kwargs.get('category'), active=False)

    if kwargs:  
        return render(request, "auctions/category.html/", {
           "categorys": get_categorys(),
           "current_category": kwargs.get('category'),
           "active_items": get_items_with_bid(kwargs.get('category')), 
           "inactive_items": get_inactive_items(kwargs.get('category'))     
    })

    return render(request, "auctions/category.html/", {
           "categorys": get_categorys()
    })


def get_items_with_bid(*args):
    # Gets a list with the items and the latest bid
    # if an category request is incoming it filters for that.

    listings = Listings.objects.filter(active=True).order_by('-pk')
    if args:
        listings = Listings.objects.filter(active=True, category=args[0]).order_by('-pk')

    items = []    
    for item in listings:
        data = {}
        data['id'] = item.pk
        data['title'] = item.title
        data['creator'] = item.creator
        data['category'] = item.category
        data['image'] = item.image
        data['description'] = item.description  
        data['bid'] = Bid.objects.get(item=item.pk).bid
        items.append(data)

    return items


def get_inactive_items(*args):    
    # Gets a list with the items and the winner with the winnng bid.
    # if an category request is incoming it filters for that.

    listings = Listings.objects.filter(active=False).order_by('-pk')
    if args:
        listings = Listings.objects.filter(active=False, category=args[0]).order_by('-pk')

    items = []    
    for item in listings:
        data = {}
        data['id'] = item.pk
        data['title'] = item.title
        data['creator'] = item.creator
        data['category'] = item.category
        data['image'] = item.image
        data['description'] = item.description 
        data['bid'] = Bid.objects.get(item=item.pk).bid
        data['winner'] = Bid.objects.get(item=item.pk).username
        items.append(data)

    return items


def get_categorys():
    # Gets all the categorys for the new_auction page
    
    categorys_choises = []
    for category in Listings.CATEGORTY_CHOICES:
        categorys_choises.append(category[0])
    
    return categorys_choises

