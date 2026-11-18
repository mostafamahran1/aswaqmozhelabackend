from django.db import models

from utils.images import optimize_model_images

class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories/')

    def save(self, *args, **kwargs):
        optimize_model_images(self, ('image',))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return ''
