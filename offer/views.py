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
    font_path = os.path.join(settings.BASE_DIR, 'static', 'ofont.ru_Plumb.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)

    background1_path = os.path.join(settings.BASE_DIR, 'img1.jpg')  # Для option1
    background2_path = os.path.join(settings.BASE_DIR, 'img2.jpg')  # Для option2
    
    # Функция для скругления углов
    def add_rounded_corners(image, radius=37):
        from PIL import ImageDraw
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius, fill=255)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        image.putalpha(mask)
        return image

    # Функция для обрезки изображения по принципу "cover"
    def resize_and_crop_cover(img, target_width, target_height):
        """
        Масштабирует и обрезает изображение для заполнения целевой области
        без искажения пропорций (аналог background-size: cover)
        """
        if target_width <= 0 or target_height <= 0:
            return img

        # Рассчитываем соотношения сторон
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        # Определяем новые размеры для масштабирования
        if img_ratio > target_ratio:
            # Подгоняем по высоте -> ширина станет больше целевой
            new_height = target_height
            new_width = int(img.width * new_height / img.height)
        else:
            # Подгоняем по ширине -> высота станет больше целевой
            new_width = target_width
            new_height = int(img.height * new_width / img.width)

        # Масштабируем
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Центрируем и обрезаем
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return img.crop((left, top, right, bottom))

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
                        # Конвертация
                        if product_img.mode != 'RGBA':
                            product_img = product_img.convert('RGBA')

                        # Жесткое задание размеров для разных вариантов
                        if option == "option1":
                            target_width = 1118
                            target_height = 2079
                            position = (124, 125)
                        else:  # option2
                            target_width = 1970
                            target_height = 1320
                            position = (1395, 120)
                        # Обрезаем и масштабируем
                        product_img = resize_and_crop_cover(product_img, target_width, target_height)
                        
                        # Скругляем углы ПОСЛЕ обрезки
                        product_img = add_rounded_corners(product_img)
                        
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
                                # Жесткие размеры для дополнительных фото
                                photo_height = 1040
                                photo_width = 604

                                x_pos = 1309
                                y_pos = 125

                                for photo_path in additional_photos:
                                    with Image.open(photo_path) as img:
                                        if img.mode != 'RGBA':
                                            img = img.convert('RGBA')
                                        
                                        # Инициализация размеров для дополнительных фото
                                        img_target_width = photo_width
                                        img_target_height = photo_height
                                        
                                        # Обрезаем и масштабируем
                                        img = resize_and_crop_cover(img, img_target_width, img_target_height)
                                        
                                        # Скругляем углы
                                        img = add_rounded_corners(img, radius=15)

                                        bg.paste(img, (x_pos, y_pos), img)
                                        
                                        y_pos += img_target_height

                        if option == "option2":
                            additional_photos = []
                            if product.additional_photo1 and os.path.exists(product.additional_photo1.path):
                                additional_photos.append(product.additional_photo1.path)
                            if product.additional_photo2 and os.path.exists(product.additional_photo2.path):
                                additional_photos.append(product.additional_photo2.path)
                            
                            if additional_photos:
                                # Определяем размеры для горизонтального расположения
                                photo_height = 700
                                photo_width = 700
                                
                                x_pos = 1970
                                y_pos = 1500
                                # Рассчитываем доступную ширину для размещения изображений
 
                                    # Располагаем изображения горизонтально
                                for photo_path in additional_photos:
                                    with Image.open(photo_path) as img:
                                        if img.mode != 'RGBA':
                                            img = img.convert('RGBA')
                                            
                                            # Обрезаем и масштабируем
                                        img = resize_and_crop_cover(img, photo_width, photo_height)
                                            
                                            # Скругляем углы
                                        img = add_rounded_corners(img, radius=15)
                                            
                                            # Вставляем изображение
                                        bg.paste(img, (x_pos, y_pos), img)
                                            
                                            # Сдвигаем позицию для следующего изображения
                                        x_pos += photo_width   # отступ между изображениями

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
                    
                    pdf.set_font('DejaVu', '', 24)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_xy(120, 110)
                    pdf.cell(0, 0, price_str, align='C', ln=True)
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
                    pdf.cell(287, 10, f" {product.dimensions}", align='C', ln=True)
                else:
                    # Вариант 2: текст слева
                    pdf.set_font('DejaVu', '', 10)
                    pdf.set_xy(20, 40)
                    pdf.cell(170, 15, product.name.upper(), ln=True)
                    
                    pdf.set_font('DejaVu', '', 24)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_xy(35, 101)
                    pdf.cell(200, 20, price_str, ln=True)
                    pdf.set_text_color(0, 0, 0)
                    
                    pdf.set_font('DejaVu', '', 12)
                    materials = product.material.split(',')
                    y_pos = 160
                    for material in materials:
                        material = material.strip()
                        pdf.set_xy(20, y_pos)
                        pdf.cell(32, 0, material, align='C', ln=True)
                        y_pos += 8
                    
                    pdf.set_xy(85, 150)
                    pdf.cell(287, 20, f"{product.dimensions}", ln=True)
                
                # Добавляем контактную информацию
                pdf.set_font('DejaVu', '', 14)
                pdf.set_text_color(0, 0, 0)
                pdf.set_xy(0, 200)
                phone_number1 = "+74951912718"
                pdf.cell(75, 0, phone_number1, link=f"tel:{phone_number1}", align='C', ln=True)

                pdf.set_xy(220, 200)
                phone_number2 = "+79627379775"
                pdf.cell(55, 0, phone_number2, link=f"tel:{phone_number2}", align='C', ln=True)

                pdf.set_xy(90, 200)
                pdf.cell(0, 0, "www.mebel-altezza.ru", ln=1, link="https://mebel-altezza.ru/")
                pdf.set_xy(160, 200)
                pdf.cell(0, 0, "info@mebel-altezza.ru", ln=1, link="mailto:info@mebel-altezza.ru")
                  
                      
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

