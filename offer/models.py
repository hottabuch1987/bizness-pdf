from django.db import models


from django.template.loader import render_to_string
from django.core.files.base import ContentFile

from django.db import models

class Material(models.Model):
    name = models.CharField("Материал", max_length=100, unique=True)  # Название материала

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

class Dimensions(models.Model):
    name = models.CharField("Название", max_length=100, blank=True, null=True)
    size = models.CharField("Габариты", max_length=100, blank=True, null=True)  # Размеры

    def __str__(self):
        return self.size if self.size else ""
    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

class Product(models.Model):
    article = models.CharField("Артикул", max_length=100, unique=True)  # Артикул
    name = models.CharField("Наименование", max_length=255)  # Наименование
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)  # Цена
    stock = models.IntegerField("Остаток")  # Остаток
    color = models.CharField("Цвет", max_length=50)  # Цвет
    main_photo = models.ImageField("Главное фото", upload_to='products/main/')  # Главное фото
    additional_photo1 = models.ImageField("Доп. фото №1", upload_to='products/additional/')  # Доп. фото 1
    additional_photo2 = models.ImageField("Доп. фото №2", upload_to='products/additional/')  # Доп. фото 2
    description = models.TextField("Описание", blank=True, null=True)  # Описание
    materials = models.ManyToManyField(Material, through='ProductMaterial', verbose_name="Материалы", blank=True, null=True)  # Связь с материалами
    dimensions = models.ManyToManyField(Dimensions, through='ProductDimensions', verbose_name="Габариты", blank=True, null=True)  # Связь с габаритами

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'material')  # Уникальная пара продукт-материал


class ProductDimensions(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    dimensions = models.ForeignKey(Dimensions, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'dimensions',)  # Уникальная пара продукт-габариты
