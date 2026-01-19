from .models import Review, Vote, Comment, Flag
from django import forms
from django.utils.translation import gettext_lazy as _


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [_("message"), _("rating")]


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = []


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [_("message")]


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = [_("flag_type")]
