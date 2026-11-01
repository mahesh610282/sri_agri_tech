from django.shortcuts import render
from .models import GalleryImage

def gallery(request):
    images = GalleryImage.objects.filter(active=True)
    return render(request, "gallery/home.html", {"images": images})
