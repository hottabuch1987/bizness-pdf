from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product
from .forms import UploadCSVForm, ProductForm
from io import TextIOWrapper
import csv

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


from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm

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

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.contrib import messages

def convert_to_pdf(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        
        if not product_ids:
            messages.warning(request, 'Выберите хотя бы один товар для экспорта в PDF')
            return redirect('product_list')
            
        products = Product.objects.filter(id__in=product_ids)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="products_export.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # Заголовок PDF
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 50, "Экспорт товаров")
        p.setFont("Helvetica", 12)
        p.drawString(100, height - 70, f"Всего товаров: {len(products)}")
        
        # Подготовка данных для таблицы
        data = [['Артикул', 'Наименование', 'Цена', 'Остаток', 'Материал', 'Цвет']]
        
        for product in products:
            data.append([
                product.article,
                product.name,
                f"{product.price} ₽",
                f"{product.stock} шт.",
                product.material,
                product.color
            ])
        
        # Создание таблицы
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Размещение таблицы на странице
        table.wrapOn(p, width - 100, height - 100)
        table.drawOn(p, 50, height - 150 - len(products)*20)
        
        p.showPage()
        p.save()
        return response

    return redirect('product_list')