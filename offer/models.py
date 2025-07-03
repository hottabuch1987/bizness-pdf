from django.db import models


class Material(models.Model):
    """
    Модель материала
    """
    name = models.CharField("Материал", max_length=100, unique=True) 

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

class Dimensions(models.Model):
    """
    Модель габаритов
    """
    name = models.CharField("Название", max_length=100, blank=True, null=True)
    size = models.CharField("Габариты", max_length=100, blank=True, null=True)  

    def __str__(self):
        return self.size if self.size else ""
    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

class Product(models.Model):
    """
    Модель товара
    """
    article = models.CharField("Артикул", max_length=100, unique=True) 
    name = models.CharField("Наименование", max_length=255)  
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2) 
    stock = models.IntegerField("Остаток") 
    color = models.CharField("Цвет", max_length=50) 
    main_photo = models.ImageField("Главное фото", upload_to='products/main/')
    additional_photo1 = models.ImageField("Доп. фото №1", upload_to='products/additional/')
    additional_photo2 = models.ImageField("Доп. фото №2", upload_to='products/additional/') 
    description = models.TextField("Описание", blank=True, null=True) 
    materials = models.ManyToManyField(Material, through='ProductMaterial', verbose_name="Материалы", blank=True, null=True) 
    dimensions = models.ManyToManyField(Dimensions, through='ProductDimensions', verbose_name="Габариты", blank=True, null=True) 

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'material') 

class ProductDimensions(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    dimensions = models.ForeignKey(Dimensions, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'dimensions',) 
