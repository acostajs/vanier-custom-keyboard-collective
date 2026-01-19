from django import forms
from django.utils.translation import gettext_lazy as _


class ProductFilterForm(forms.Form):
    SORT_CHOICES = [
        ("new-old", _("Newest first")),
        ("old-new", _("Oldest first")),
        ("price-high-low", _("Price: High to low")),
        ("price-low-high", _("Price: Low to high")),
        ("discount-high-low", _("Discount: High to low")),
        ("discount-low-high", _("Discount: Low to high")),
        ("a-z", _("A to Z")),
        ("z-a", _("Z to A")),
        ("rating-high-low", _("Rating: High to Low")),
    ]

    FILTER_CHOICES = [
        ("quantity", _("Availability")),
        ("discount_percentage", _("With Discount")),
        ("created_recently", _("Created Recently")),
    ]

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial="new-old",
        label=_("Sort by"),
    )

    filter_criteria = forms.MultipleChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label=_("Filters"),
    )


class SearchForm(forms.Form):
    search = forms.CharField(
        required=True,
        max_length=200,
        label=_("Search"),
    )
