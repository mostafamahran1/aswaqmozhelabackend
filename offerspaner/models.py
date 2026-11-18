from django.db import models

from utils.images import optimize_model_images

class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/')
    # 👈 الحقول الجديدة لربط المنتج
    product_id = models.IntegerField(null=True, blank=True, help_text="ID المنتج المرتبط بالبانر")
    category_name = models.CharField(max_length=100, null=True, blank=True, help_text="اسم موديل أو قسم المنتج")

    def save(self, *args, **kwargs):
        optimize_model_images(self, ('image',))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class TopBannerImage(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان الإعلان")
    image = models.ImageField(upload_to='top_banners/', verbose_name="صورة البانر")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "صورة البانر العلوي"
        verbose_name_plural = "إعلانات البانر العلوي"

    def save(self, *args, **kwargs):
        optimize_model_images(self, ('image',))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title