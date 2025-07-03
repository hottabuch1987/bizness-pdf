import csv
import os
import tempfile
from io import TextIOWrapper

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from fpdf import FPDF
from PIL import Image

from .forms import UploadCSVForm, ProductForm
from .models import Product, Material, Dimensions, ProductMaterial, ProductDimensions
from .utils import resize_and_crop_cover, add_rounded_corners, process_option1, process_option2, add_contacts


def convert_to_pdf(request):
    # Генерация PDF
    if request.method != 'POST':
        return redirect('product_list')
    
    selected_ids = request.POST.getlist('product_ids')
    if not selected_ids:
        messages.error(request, "Выберите хотя бы один товар.")
        return redirect('product_list')

    # Инициализация PDF
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False, margin=0)

    # Настройка шрифтов
    font_path = os.path.join(settings.BASE_DIR, 'static', 'Plumb.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)
    font_path_bild = os.path.join(settings.BASE_DIR, 'static', 'Plumb_bold.ttf')
    pdf.add_font('DejaVu', 'B', font_path_bild, uni=True)
    
    BACKGROUND1_PATH = os.path.join(settings.BASE_DIR, 'img1.jpg')
    BACKGROUND2_PATH = os.path.join(settings.BASE_DIR, 'img2.jpg')

    with tempfile.TemporaryDirectory() as temp_dir:
        for product_id in selected_ids:
            product = get_object_or_404(Product, id=product_id)
            if not product.main_photo:
                continue
                
            option = request.POST.get(f'option_{product_id}', 'option1')
            bg_path = BACKGROUND1_PATH if option == 'option1' else BACKGROUND2_PATH
            
            try:
                with Image.open(bg_path) as bg:
                    bg = bg.convert("RGBA")
                    
                    if option == "option1":
                        result_image = process_option1(
                            product, 
                            bg, 
                            font_path,
                            resize_and_crop_cover,
                            add_rounded_corners      
                        )
                    else:
                        result_image = process_option2(
                            product, 
                            bg, 
                            font_path,
                            resize_and_crop_cover,
                            add_rounded_corners      
                        )

                    # Сохранение временного изображения
                    temp_img = os.path.join(temp_dir, f'comp_{product_id}.jpg')
                    result_image.convert('RGB').save(temp_img, quality=95)
                
                # Добавление страницы в PDF
                pdf.add_page()
                pdf.image(temp_img, x=0, y=0, w=297, h=210)
                add_contacts(pdf)
                      
            except Exception as e:
                print(f"Ошибка обработки товара {product_id}: {e}")
                continue

        # Генерация PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="catalog.pdf"'
        pdf_output = pdf.output(dest='S').encode('latin1')
        response.write(pdf_output)
        return response


def upload_csv(request):
    # Обработка загрузки CSV
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            try:
                csv_file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8-sig')
                csv_reader = csv.DictReader(csv_file_wrapper, delimiter=';')
                csv_reader.fieldnames = [name.strip('\ufeff').strip() for name in csv_reader.fieldnames if name]
                
                created_count = 0
                errors = []
                
                for i, row in enumerate(csv_reader, start=1):
                    row = {k.strip('\ufeff').strip(): v.strip() for k, v in row.items() if k and k.strip()}
                    
                    try:
                        required_fields = ['Артикул', 'Наименование', 'Цена', 'Остаток', 'Цвет']
                        if not all(field in row for field in required_fields):
                            missing = set(required_fields) - set(row.keys())
                            raise ValueError(f"Отсутствуют поля: {', '.join(missing)}")
                        
                        # Основные данные продукта
                        product_data = {
                            'article': row['Артикул'],
                            'name': row['Наименование'],
                            'price': float(row['Цена'].replace(',', '.')),
                            'stock': int(row['Остаток']),
                            'color': row['Цвет'],
                            'description': row.get('Описание', ''),
                        }
                        
                        # Создаем/обновляем продукт
                        product, created = Product.objects.update_or_create(
                            article=product_data['article'],
                            defaults=product_data
                        )
                        
                        # Обработка материалов
                        if 'Материал' in row and row['Материал']:
                            # Удаляем старые материалы
                            ProductMaterial.objects.filter(product=product).delete()
                            
                            materials = [m.strip() for m in row['Материал'].split(',')]
                            for material_name in materials:
                                material, _ = Material.objects.get_or_create(name=material_name)
                                ProductMaterial.objects.get_or_create(
                                    product=product, 
                                    material=material
                                )
                        
                        # Обработка габаритов
                        if 'Габариты' in row and row['Габариты']:
                            # Удаляем старые габариты
                            ProductDimensions.objects.filter(product=product).delete()
                            
                            dimensions_list = [d.strip() for d in row['Габариты'].split(',')]
                            for dimension_size in dimensions_list:
                                dimension, _ = Dimensions.objects.get_or_create(size=dimension_size)
                                ProductDimensions.objects.get_or_create(
                                    product=product,
                                    dimensions=dimension
                                )
                        
                        if created:
                            created_count += 1
                            
                    except Exception as e:
                        errors.append(f"Строка {i}: {str(e)}")
                        continue
                
                if errors:
                    messages.warning(request, f"Успешно загружено {created_count} товаров, ошибки: {len(errors)}")
                else:
                    messages.success(request, f'Успешно загружено {created_count} товаров')
                
                return redirect('product_list')
            
            except Exception as e:
                messages.error(request, f'Ошибка при обработке файла: {str(e)}')
    else:
        form = UploadCSVForm()
    
    return render(request, 'offer/upload_csv.html', {'form': form})


def product_list(request):
    # Получение списка продуктов
    products = Product.objects.prefetch_related('materials', 'dimensions').all()
    return render(request, 'offer/product_list.html', {'products': products})


def edit_product(request, product_id):
    # Редактирование продукта
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Обработка материалов
            materials_str = form.cleaned_data.get('materials_input', '')
            materials_list = [m.strip() for m in materials_str.split(',') if m.strip()]
            
            ProductMaterial.objects.filter(product=product).delete()
            for material_name in materials_list:
                material, _ = Material.objects.get_or_create(name=material_name)
                ProductMaterial.objects.get_or_create(product=product, material=material)

            dimensions_str = form.cleaned_data.get('dimensions_input', '')
            dimensions_name_str = form.cleaned_data.get('dimensions_name_input', '')
            
            # Создаем списки значений
            dimensions_list = [d.strip() for d in dimensions_str.split(',') if d.strip()]
            dimensions_name_list = [n.strip() for n in dimensions_name_str.split(',') if n.strip()]

            ProductDimensions.objects.filter(product=product).delete()
            
            for i, dimension_size in enumerate(dimensions_list):
                name = dimensions_name_list[i] if i < len(dimensions_name_list) else ''
                
                dimension, _ = Dimensions.objects.get_or_create(
                    size=dimension_size,
                    defaults={'name': name} 
                )

                if dimension.name != name:
                    dimension.name = name
                    dimension.save()
                
                ProductDimensions.objects.create(
                    product=product,
                    dimensions=dimension
                )
            
            messages.success(request, 'Товар успешно обновлен')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'offer/edit_product.html', {
        'form': form,
        'product': product
    })


def delete_products(request):
    # Удаление продуктов
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        Product.objects.filter(id__in=product_ids).delete()
        return HttpResponse(status=200)
    return HttpResponse(status=400)

