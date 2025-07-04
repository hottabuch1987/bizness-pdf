from django.db import models

class Product(models.Model):
    article = models.CharField("Артикул", max_length=100, unique=True)
    name = models.CharField("Наименование", max_length=255)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    stock = models.IntegerField("Остаток")
    color = models.CharField("Цвет", max_length=50)
    main_photo = models.ImageField("Главное фото", upload_to='products/main/')
    additional_photo1 = models.ImageField("Доп. фото №1", upload_to='products/additional/')
    additional_photo2 = models.ImageField("Доп. фото №2", upload_to='products/additional/')
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']

    def __str__(self):
        return self.name

class Material(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='materials'
    )
    name = models.CharField("Материал", max_length=100)

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ['id']

    def __str__(self):
        return self.name

class Dimension(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='dimensions'
    )
    name = models.CharField("Название", max_length=100, blank=True, null=True)
    value = models.CharField("Значение", max_length=100)

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
        ordering = ['id']

    def __str__(self):
        return f"{self.name}: {self.value}" if self.name else self.value