from django.contrib import admin
from .models import GalleryImage

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "image_type", "active", "created_at")
    list_filter = ("image_type", "active")
    search_fields = ("title",)
