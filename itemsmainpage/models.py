from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return ''
