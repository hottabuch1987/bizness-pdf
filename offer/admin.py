from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.core.files import File
from io import TextIOWrapper
import csv

from .models import Product

class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV файл')
    actions = ['generate_pdf_action']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('article', 'name', 'price', 'stock')
    change_list_template = 'admin/products_change_list.html'
    change_form_template = 'admin/product_change_form.html'
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv, name='import-csv'),
            path('<path:object_id>/generate-pdf/', self.generate_pdf_view, name='generate_pdf'),
        ]
        return custom_urls + urls
    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES['csv_file']
            
            # Читаем файл с правильной кодировкой
            file_data = csv_file.read().decode('utf-8-sig')  # utf-8-sig для обработки BOM
            lines = file_data.split('\n')
            
            # Создаем CSV reader с правильным разделителем
            reader = csv.DictReader(lines, delimiter=';')
            
            created = 0
            updated = 0
            
            for row in reader:
                if not row:  # Пропускаем пустые строки
                    continue
                    
                try:
                    article = row.get('Артикул', '')
                    if not article:  # Пропускаем строки без артикула
                        continue
                        
                    defaults = {
                        'name': row.get('Наименование', ''),
                        'price': float(row.get('Цена', 0)),
                        'stock': int(row.get('Остаток', 0)),
                        'material': row.get('Материал', ''),
                        'color': row.get('Цвет', '').strip(),
                        'dimensions': row.get('Габариты', ''),
                       
                    }
                    
                    obj, created_flag = Product.objects.update_or_create(
                        article=article,
                        defaults=defaults
                    )
                    
                    if created_flag:
                        created += 1
                    else:
                        updated += 1
                        
                except Exception as e:
                    messages.error(
                        request,
                        f"Ошибка при обработке строки: {row}. Ошибка: {str(e)}"
                    )
                    continue
            
            messages.success(
                request,
                f"Импорт завершен. Создано: {created}, обновлено: {updated}"
            )
            return redirect("..")
        
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_import_form.html", payload
        )
    
 
    
    
    def generate_pdf_view(self, request, object_id):
        product = Product.objects.get(id=object_id)
        pdf_file = product.generate_pdf()
        
        # Если хотите сразу скачать файл:
        from django.http import FileResponse
        response = FileResponse(pdf_file.open(), as_attachment=True, filename=f'product_{product.article}.pdf')
        return response
    
    def generate_pdf_action(self, request, queryset):
        for product in queryset:
            product.generate_pdf()
        self.message_user(request, f"PDF сгенерированы для {queryset.count()} товаров")
    generate_pdf_action.short_description = "Сгенерировать PDF"

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_pdf_button'] = True
        return super().changeform_view(request, object_id, form_url, extra_context)
    