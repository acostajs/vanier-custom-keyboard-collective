from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from review.models import Review
from .forms import ProductFilterForm
from django.db.models import Count


def index(request):
    """Display Home, showing the different products and categories."""
    sort_criteria = request.GET.get("sort", "created_date")
    filter_criteria_list = request.GET.getlist("filter_criteria")

    filtered = Product.filter_by(filter_criteria_list)
    products = Product.sort_by(sort_criteria, products=filtered)

    categories = Category.objects.order_by("name")

    filter_sort_form = ProductFilterForm(
        initial={"sort": sort_criteria, "filter_criteria": filter_criteria_list}
    )
    context = {
        "categories": categories,
        "products": products,
        "current_sort": sort_criteria,
        "filter_sort_form": filter_sort_form,
        "current_filters": filter_criteria_list,
    }

    return render(request, "inventory/index.html", context)


def category(request, category_id):
    """Display Category Detail page, showing all the products inside a single category."""
    category = get_object_or_404(Category, pk=category_id)
    sort_criteria = request.GET.get("sort", "created_date")
    filter_criteria_list = request.GET.getlist("filter_criteria")

    base_qs = category.product_set.all()
    filtered = Product.filter_by(filter_criteria_list, products=base_qs)
    products = Product.sort_by(sort_criteria, products=filtered)

    filter_sort_form = ProductFilterForm(
        initial={"sort": sort_criteria, "filter_criteria": filter_criteria_list}
    )

    context = {
        "category": category,
        "products": products,
        "current_sort": sort_criteria,
        "filter_sort_form": filter_sort_form,
        "current_filters": filter_criteria_list,
    }
    return render(request, "inventory/category.html", context)


def product(request, product_id):
    """Display Product Detail page, showing all the details of the product."""
    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.annotate(votes_count=Count("votes")).order_by(
        "-votes_count"
    )
    rating_average = Review.rating_average(product)
    category = product.category
    products = category.product_set.all()
    context = {
        "product": product,
        "category": category,
        "products": products,
        "reviews": reviews,
        "rating_average": rating_average,
    }
    return render(request, "inventory/product.html", context)


def results(request):
    """Display the search results done by the user."""
    search_query = request.GET.get("search", "")
    products = Product.search_by_name(search_query)

    sort_criteria = request.GET.get("sort", "created_date")
    filter_criteria_list = request.GET.getlist("filter_criteria")

    filtered = Product.filter_by(filter_criteria_list, products=products)
    products = Product.sort_by(sort_criteria, products=filtered)

    context = {
        "products": products,
        "current_search": search_query,
    }
    return render(request, "inventory/results.html", context)
