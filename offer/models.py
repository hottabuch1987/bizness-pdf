from django.db import models


from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from io import BytesIO

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
    pdf_file = models.FileField(upload_to='product_pdfs/', blank=True, null=True, verbose_name='PDF файл')
    
    @property
    def image_url(self):
        if self.main_photo and hasattr(self.main_photo, 'url'):
            return self.main_photo.url
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name
    
    
    
    def generate_pdf(self):
        # Подготовка данных для шаблона
        context = {
            'product': self,
            'price_formatted': f"{self.price:,.2f} руб.".replace(',', ' '),
        }
        
        # Генерация HTML из шаблона
        html_string = render_to_string('admin/product_template.html', context)
        
        # Создание PDF из HTML
        buffer = BytesIO()
        pdf = pisa.CreatePDF(html_string, dest=buffer)
        
        if pdf.err:
            return None  # Обработка ошибок, если PDF не был создан
        
        buffer.seek(0)  # Переместить указатель в начало буфера
        
        # Сохранение PDF в поле модели
        self.pdf_file.save(f'product_{self.article}.pdf', ContentFile(buffer.getvalue()))
        self.save()
        return self.pdf_file