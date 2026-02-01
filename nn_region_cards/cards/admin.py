from django.contrib import admin
from .models import CityCard


@admin.register(CityCard)
class CityCardAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "author", "views_count", "created_at")
    search_fields = ("title", "region", "slug", "author__username")
    list_filter = ("region", "created_at")
    prepopulated_fields = {"slug": ("title",)}
