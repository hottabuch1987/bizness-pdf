from django.contrib import messages
import csv
import os
import tempfile
from io import TextIOWrapper

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from fpdf import FPDF
from PIL import Image

from .forms import UploadCSVForm, ProductForm, MaterialFormSet, DimensionFormSet
from .models import Product, Material, Dimension
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
                updated_count = 0
                errors = []
                
                for i, row in enumerate(csv_reader, start=1):
                    row = {k.strip('\ufeff').strip(): v.strip() for k, v in row.items() if k and k.strip()}
                    
                    try:
                        # Проверка обязательных полей
                        required_fields = ['Артикул', 'Наименование', 'Цена', 'Остаток', 'Цвет']
                        missing_fields = [field for field in required_fields if field not in row]
                        if missing_fields:
                            raise ValueError(f"Отсутствуют поля: {', '.join(missing_fields)}")
                        
                        # Подготовка данных продукта
                        product_data = {
                            'article': row['Артикул'],
                            'name': row['Наименование'],
                            'price': float(row['Цена'].replace(',', '.').replace(' ', '')),
                            'stock': int(row['Остаток'].replace(' ', '')),
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
                            # Удаляем старые материалы продукта
                            Material.objects.filter(product=product).delete()
                            
                            # Создаем новые материалы
                            materials = [m.strip() for m in row['Материал'].split(',') if m.strip()]
                            for material_name in materials:
                                Material.objects.create(
                                    product=product,
                                    name=material_name
                                )
                        
                        # Обработка габаритов
                        if 'Габариты' in row and row['Габариты']:
                            # Удаляем старые габариты продукта
                            Dimension.objects.filter(product=product).delete()
                            
                            # Создаем новые габариты
                            dimensions = [d.strip() for d in row['Габариты'].split(',') if d.strip()]
                            for dimension_value in dimensions:
                                Dimension.objects.create(
                                    product=product,
                                    value=dimension_value
                                )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                            
                    except Exception as e:
                        errors.append(f"Строка {i}: {str(e)}")
                        continue
                
                # Формируем сообщение о результате
                if created_count or updated_count:
                    msg = f"Успешно обработано товаров: {created_count + updated_count} "
                    msg += f"(новых: {created_count}, обновлено: {updated_count})"
                    
                    if errors:
                        msg += f" | Ошибок: {len(errors)}"
                        messages.warning(request, msg)
                    else:
                        messages.success(request, msg)
                elif errors:
                    messages.error(request, f"Все строки содержат ошибки. Ошибок: {len(errors)}")
                
                # Сохраняем ошибки в сессии для детализации
                if errors:
                    request.session['upload_errors'] = errors
                
                return redirect('product_list')
            
            except Exception as e:
                messages.error(request, f'Ошибка при обработке файла: {str(e)}')
    else:
        form = UploadCSVForm()
    
    return render(request, 'offer/upload_csv.html', {'form': form})


def product_list(request):
    # Получение списка всех продуктов
    products_list = Product.objects.prefetch_related('materials', 'dimensions').all()
    
    # Настройка пагинации
    paginator = Paginator(products_list, 15)  # Показывать 15 товаров на странице
    page = request.GET.get('page')  # Получаем номер текущей страницы из параметра запроса
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # Если параметр page не целое число, показываем первую страницу
        products = paginator.page(1)
    except EmptyPage:
        # Если страница вне диапазона (например, 9999), показываем последнюю страницу
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'offer/product_list.html', {'products': products})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        material_formset = MaterialFormSet(request.POST, instance=product, prefix='materials')
        dimension_formset = DimensionFormSet(request.POST, instance=product, prefix='dimensions')
        
        if form.is_valid() and material_formset.is_valid() and dimension_formset.is_valid():
            form.save()
            material_formset.save()
            dimension_formset.save()
            messages.success(request, 'Товар успешно обновлен')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
        material_formset = MaterialFormSet(instance=product, prefix='materials')
        dimension_formset = DimensionFormSet(instance=product, prefix='dimensions')
    
    return render(request, 'offer/edit_product.html', {
        'form': form,
        'material_formset': material_formset,
        'dimension_formset': dimension_formset,
        'product': product
    })



def delete_products(request):
    # Удаление продуктов
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        Product.objects.filter(id__in=product_ids).delete()
        return HttpResponse(status=200)
    return HttpResponse(status=400)