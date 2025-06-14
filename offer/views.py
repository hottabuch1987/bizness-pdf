from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from .forms import UploadCSVForm, ProductForm
from io import TextIOWrapper
import csv

from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect

from fpdf import FPDF
from PIL import Image
import os
import tempfile


def convert_to_pdf(request):
    if request.method != 'POST':
        return redirect('product_list')
    
    selected_ids = request.POST.getlist('product_ids')
    if not selected_ids:
        messages.error(request, "Выберите хотя бы один товар.")
        return redirect('product_list')

    # Инициализация PDF с альбомной ориентацией
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False, margin=0)
    
    # Настройка шрифтов
    #font_path = os.path.join(settings.STATIC_ROOT, 'DejaVuSansCondensed-Bold.ttf')
    font_path = os.path.join(settings.STATIC_ROOT, 'dejavu-fonts-ttf/ttf/DejaVuSansCondensed-Bold.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)

    background1_path = os.path.join(settings.BASE_DIR, 'img1.jpg')  # Для option1
    background2_path = os.path.join(settings.BASE_DIR, 'img2.jpg')  # Для option2
    
    # Функция для скругления углов
    def add_rounded_corners(image, radius=20):
        from PIL import ImageDraw
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius, fill=255)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        image.putalpha(mask)
        return image

    with tempfile.TemporaryDirectory() as temp_dir:
        for product_id in selected_ids:
            product = get_object_or_404(Product, id=product_id)
            if not product.main_photo:
                continue
                
            option = request.POST.get(f'option_{product_id}', 'option1')
            bg_path = background1_path if option == 'option1' else background2_path
            
            try:
                # Создаем композицию изображения
                with Image.open(bg_path) as bg:
                    bg = bg.convert("RGBA")
                    bg_width, bg_height = bg.size
                    
                    # Обработка главного изображения
                    with Image.open(product.main_photo.path) as product_img:
                        # Конвертация и скругление углов
                        if product_img.mode == 'RGBA':
                            product_img = add_rounded_corners(product_img)
                        else:
                            product_img = product_img.convert('RGBA')
                            product_img = add_rounded_corners(product_img)
                        
                        # Жесткое задание размеров для разных вариантов
                        if option == "option1":
                            # Жесткие размеры: 70% ширины и 50% высоты фона
                            target_width = int(bg_width * 0.29) + 80
                            target_height = int(bg_height * 0.8) + 40
                            
                            # Растягивание до точных размеров
                            product_img = product_img.resize((target_width, target_height), Image.LANCZOS)
                            
                            # Позиционирование
                            position = (
                                (bg_width - target_width) // 2 - 470,  # Центр по X
                                int(bg_height * 0.075)             # 5% от высоты сверху
                            )
                        else:  # option2
                            # Жесткие размеры: 50% ширины и 70% высоты фона
                            target_width = int(bg_width * 0.5) + 150
                            target_height = int(bg_height * 0.57)
                            
                            # Растягивание до точных размеров
                            product_img = product_img.resize((target_width, target_height), Image.LANCZOS)
                            
                            position = (
                                bg_width - target_width - 35,  # Справа с отступом
                                (bg_height - target_height) - 330  # Центр по Y
                            )
                        
                        # Наложение на фон
                        bg.paste(product_img, position, product_img)
                        
                        # Обработка дополнительных изображений
                        additional_photos = []
                        if option == "option1":
                            if product.additional_photo1 and os.path.exists(product.additional_photo1.path):
                                additional_photos.append(product.additional_photo1.path)
                            if product.additional_photo2 and os.path.exists(product.additional_photo2.path):
                                additional_photos.append(product.additional_photo2.path)
                                
                            if additional_photos:
                                sidebar_width = int(bg_width * 0.18)
                                sidebar_x = int(bg_width * 0.38)
                                content_y = int(bg_height * 0.07)
                                
                                # Жесткие размеры для дополнительных фото
                                photo_height = int(bg_height * 0.30) + 115
                                photo_width = sidebar_width
                                margin_y = 25
                                
                                y_pos = content_y
                                for photo_path in additional_photos:
                                    with Image.open(photo_path) as img:
                                        if img.mode != 'RGBA':
                                            img = img.convert('RGBA')
                                        img = add_rounded_corners(img, radius=15)
                                        
                                        # Растягивание до точных размеров
                                        img = img.resize((photo_width, photo_height), Image.LANCZOS)
                                        
                                        # Позиционирование
                                        x_pos = sidebar_x
                                        bg.paste(img, (x_pos, y_pos), img)
                                        
                                        y_pos += photo_height + margin_y - 30

                            #
                            
                        elif option == "option2":
                            additional_photos = []
                            if product.additional_photo1 and os.path.exists(product.additional_photo1.path):
                                additional_photos.append(product.additional_photo1.path)
                            if product.additional_photo2 and os.path.exists(product.additional_photo2.path):
                                additional_photos.append(product.additional_photo2.path)
                                
                            if additional_photos:
                                footer_height = int(bg_height * 0.34) 
                                footer_y = bg_height - footer_height
                                total_width = bg_width 
                                num_photos = len(additional_photos)
                                margin_x = 0
                                margin_y = 35
                                
                                # Жесткие размеры для дополнительных фото
                                photo_width = ((total_width - (num_photos) * margin_x) // num_photos) - 420
                                photo_height = footer_height - 2 * margin_y
                                
                                x_pos = margin_x + 790
                                for photo_path in additional_photos:
                                    with Image.open(photo_path) as img:
                                        if img.mode != 'RGBA':
                                            img = img.convert('RGBA')
                                        img = add_rounded_corners(img, radius=15)
                                        
                                        # Растягивание до точных размеров
                                        img = img.resize((photo_width, photo_height), Image.LANCZOS)
                                        
                                        # Позиционирование
                                        y_pos = footer_y  
                                        bg.paste(img, (x_pos, y_pos), img)
                                        
                                        x_pos += photo_width + margin_x 
                            
                        # Сохраняем временное изображение
                        temp_img = os.path.join(temp_dir, f'comp_{product_id}.jpg')
                        bg.convert('RGB').save(temp_img, quality=95)
                
                # Добавляем страницу в PDF
                pdf.add_page()
                
                # Фоновое изображение (на всю страницу)
                pdf.image(temp_img, x=0, y=0, w=297, h=210)
                
                # Форматирование цены
                price_value = product.price
                price_str = f"{price_value:,.2f}".replace(',', ' ').replace('.', ',') + " руб."
                
                # Различное позиционирование текста
                if option == 'option1':
                    # Вариант 1: текст по центру
                    pdf.set_font('DejaVu', '', 10)
                    pdf.set_xy(70, 40)
                    pdf.cell(287, 15, product.name.upper(), align='C', ln=True)
                    
                    pdf.set_font('DejaVu', '', 20)
                    pdf.set_text_color(220, 50, 50)
                    pdf.set_xy(80, 104)
                    pdf.cell(297, 20, price_str, align='C', ln=True)
                    pdf.set_text_color(0, 0, 0)
                    
                    pdf.set_font('DejaVu', '', 12)
                    materials = product.material.split(',')
                    y_pos = 150
                    for material in materials:
                        material = material.strip()
                        pdf.set_xy(47, y_pos)
                        pdf.cell(297, 10, material, align='C', ln=True)
                        y_pos += 8
                    
                    pdf.set_xy(100, 150)
                    pdf.cell(297, 10, f" {product.dimensions}", align='C', ln=True)
                else:
                    # Вариант 2: текст слева
                    pdf.set_font('DejaVu', '', 10)
                    pdf.set_xy(20, 40)
                    pdf.cell(170, 15, product.name.upper(), ln=True)
                    
                    pdf.set_font('DejaVu', '', 20)
                    pdf.set_text_color(220, 50, 50)
                    pdf.set_xy(40, 108)
                    pdf.cell(200, 20, price_str, ln=True)
                    pdf.set_text_color(0, 0, 0)
                    
                    pdf.set_font('DejaVu', '', 12)
                    materials = product.material.split(',')
                    y_pos = 160
                    for material in materials:
                        material = material.strip()
                        pdf.set_xy(20, y_pos)
                        pdf.cell(40, 0, material, align='C', ln=True)
                        y_pos += 8
                    
                    pdf.set_xy(85, 150)
                    pdf.cell(297, 10, f"{product.dimensions}", ln=True)
                        
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


def delete_products(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        Product.objects.filter(id__in=product_ids).delete()
        return HttpResponse(status=200)
    return HttpResponse(status=400)

