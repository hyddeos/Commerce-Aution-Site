from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_auction", views.new_auction, name="new_auction"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:item_id>", views.watchlist_func, name="watchlist_func"),
    path("item/<str:item_id>", views.item, name="item"),
    path("comment/<int:item_id>", views.comment, name="comment"),
    path("category/", views.category, name="category"),
    path("category/<str:category>", views.category, name="category"), 
]
