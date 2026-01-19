from django.urls import path
from . import views

app_name = "inventory"
urlpatterns = [
    path("", views.index, name="index"),
    path("category/<int:category_id>/", views.category, name="category"),
    path("product/<int:product_id>/", views.product, name="product"),
    path("results/", views.results, name="results"),
]
