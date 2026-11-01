from django.urls import path
from .views import gallery
app_name = "gallery"
urlpatterns = [path("", gallery, name="home")]
