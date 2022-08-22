from datetime import datetime
from pyexpat import model
from sre_constants import CATEGORY
from tkinter import CASCADE
from unicodedata import category
from xml.etree.ElementTree import Comment
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
        pass


class Listings(models.Model):

    CATEGORTY_CHOICES = ( 
        ('Shoes','Shoes'),
        ('Cloths', 'Cloths'),
        ('Music','Music'),
        ('Other', 'Other'),
    )

    title = models.CharField(max_length=64)
    category = models.CharField(max_length=32, choices = CATEGORTY_CHOICES)
    image = models.CharField(max_length=300, blank=True)
    description = models.CharField(max_length=600, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creators")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"ID:{self.pk} - {self.title}, {self.category}, {self.creator}"


class Watchlist(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userwatchlist")
    watch = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="watching")
    
    def __str__(self):
        return f"{self.watch}"

class Bid(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userbidder")
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bid_item")
    bid = models.IntegerField()

    def __str__(self):
        return f"Item: {self.item}  Bid: {self.bid} Bidder: {self.username}"

class Comment(models.Model):
    comment = models.CharField(max_length=512)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="about")
    datetime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"Author: {self.username}  About: {self.item} datetime: {self.datetime} Comment: {self.comment}"



