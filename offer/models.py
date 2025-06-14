from django.db import models


from django.template.loader import render_to_string
from django.core.files.base import ContentFile


class Product(models.Model):
    article = models.CharField("Артикул", max_length=100, unique=True)  # Артикул
    name = models.CharField("Наименование", max_length=255)  # Наименование
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)  # Цена
    stock = models.IntegerField("Остаток" )  # Остаток
    material = models.CharField("Материал",  max_length=100)  # Материал
    color = models.CharField("Цвет", max_length=50)  # Цвет
    dimensions = models.CharField("Габариты", max_length=100)  # Габариты
    main_photo = models.ImageField("Главное фото", upload_to='products/main/')  # Главное фото
    additional_photo1 = models.ImageField("Доп. фото №1", upload_to='products/additional/')  # Доп. фото 1
    additional_photo2 = models.ImageField("Доп. фото №2", upload_to='products/additional/')  # Доп. фото 2
    
    
    @property
    def image_url(self):
        if self.main_photo and hasattr(self.main_photo, 'url'):
            return self.main_photo.url
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name
    
    @property
    def main_photo_url(self):
        if self.main_photo and hasattr(self.main_photo, 'url'):
            return self.main_photo.url
        return None
    
    @property
    def additional_photos(self):
        photos = []
        if self.additional_photo1 and hasattr(self.additional_photo1, 'url'):
            photos.append(self.additional_photo1.url)
        if self.additional_photo2 and hasattr(self.additional_photo2, 'url'):
            photos.append(self.additional_photo2.url)