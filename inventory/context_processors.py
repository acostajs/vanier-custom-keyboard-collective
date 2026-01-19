from .models import Category
from .forms import SearchForm


def categories_processor(request):
    categories = Category.objects.all()
    return {"categories": categories, "search_form": SearchForm()}
