from django.contrib import admin
from .models import Review, Vote, Comment, Flag

admin.site.register(Review)
admin.site.register(Vote)
admin.site.register(Comment)
admin.site.register(Flag)
