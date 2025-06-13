from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from .forms import UploadCSVForm, ProductForm
from io import TextIOWrapper
import csv

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            try:
                # Чтение CSV с учетом BOM и правильным разделителем
                csv_file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8-sig')  # Используем utf-8-sig для автоматического удаления BOM
                csv_reader = csv.DictReader(csv_file_wrapper, delimiter=';')
                
                # Удаление пустых ключей (которые могут появиться из-за лишних разделителей)
                csv_reader.fieldnames = [name.strip('\ufeff') for name in csv_reader.fieldnames if name]
                
                created_count = 0
                errors = []
                
                for i, row in enumerate(csv_reader, start=1):
                    # Очистка строки от пустых значений
                    row = {k.strip('\ufeff').strip(): v.strip() for k, v in row.items() if k and k.strip()}
                    
                    try:
                        # Проверка обязательных полей
                        required_fields = ['Артикул', 'Наименование', 'Цена', 'Остаток', 'Материал', 'Цвет']
                        if not all(field in row for field in required_fields):
                            missing = set(required_fields) - set(row.keys())
                            raise ValueError(f"Отсутствуют поля: {', '.join(missing)}")
                        
                        # Преобразование данных
                        price = float(row['Цена'].replace(',', '.'))
                        stock = int(row['Остаток'])
                        
                        # Подготовка данных для модели
                        product_data = {
                            'article': row['Артикул'],
                            'name': row['Наименование'],
                            'price': price,
                            'stock': stock,
                            'material': row['Материал'],
                            'color': row['Цвет'],
                            'dimensions': row.get('Габариты', ''),
                        }
                        
                        # Создание или обновление продукта
                        product, created = Product.objects.update_or_create(
                            article=product_data['article'],
                            defaults=product_data
                        )
                        
                        if created:
                            created_count += 1
                            
                    except Exception as e:
                        errors.append(f"Строка {i}: {e}")
                        continue
                
                if errors:
                    messages.warning(request, f"Успешно загружено {created_count} товаров, но возникли ошибки:<br>" + "<br>".join(errors))
                else:
                    messages.success(request, f'Успешно загружено {created_count} товаров')
                
                return redirect('product_list')
            
            except Exception as e:
                messages.error(request, f'Ошибка при обработке файла: {str(e)}')
    else:
        form = UploadCSVForm()
    
    return render(request, 'offer/upload_csv.html', {'form': form})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'offer/product_list.html', {'products': products})




def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'offer/edit_product.html', {
        'form': form,
        'product': product
    })



def convert_to_pdf(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        
        if not product_ids:
            messages.warning(request, 'Выберите хотя бы один товар для экспорта в PDF')
            return redirect('product_list')
            
        products = Product.objects.filter(id__in=product_ids)
        
        # Рендеринг HTML шаблона
        html_string = render_to_string(
            'offer/pdf_template.html',
            {'products': products}
        )
        
        # Настройки для WeasyPrint
        font_config = FontConfiguration()
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        
        # Генерация PDF
        pdf_file = html.write_pdf(font_config=font_config)
        
        # Создание HTTP ответа
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="products_export.pdf"'
        return response

    return redirect('product_list')



def simple_page(request):
    product = Product.objects.first()
   
    context = {
    'product': product
    }
    return render(request, 'offer/product.html', context)