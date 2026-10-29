
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("article/<int:pk>/", views.article_detail, name="article_detail"),
    path("article/create/", views.article_create, name="article_create"),
    path("article/<int:pk>/edit/", views.article_edit, name="article_edit"),
    path("article/<int:pk>/delete/", views.article_delete, name="article_delete"),
    path("article/<int:pk>/vote/", views.vote_article, name="vote_article"),
    path("article/<int:pk>/rate/", views.rate_article, name="rate_article"),
    path("article/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("popular/", views.popular_articles, name="popular"),
    path("categories/", views.category_list, name="categories"),
    path("category/<int:pk>/", views.category_detail, name="category_detail"),
    path("authors/", views.author_list, name="authors"),
    path("favorites/", views.favorite_list, name="favorites"),
]
