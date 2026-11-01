from django.db import models

class GalleryImage(models.Model):
    class ImageType(models.TextChoices):
        STORE = "STORE", "Store"
        PRODUCT = "PRODUCT", "Product"

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="gallery/")
    image_type = models.CharField(max_length=20, choices=ImageType.choices)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
