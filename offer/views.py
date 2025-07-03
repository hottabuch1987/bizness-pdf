import csv
import os
import tempfile
from io import TextIOWrapper

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from fpdf import FPDF

from .forms import UploadCSVForm, ProductForm
from .models import Product, Material, Dimensions, ProductMaterial, ProductDimensions
from .utils import resize_and_crop_cover, add_rounded_corners, smart_wrap


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
    font_path = os.path.join(settings.BASE_DIR, 'static', 'Plumb.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)
    font_path_bild = os.path.join(settings.BASE_DIR, 'static', 'Plumb_bold.ttf')
    pdf.add_font('DejaVu', 'B', font_path_bild, uni=True)
    BACKGROUND1_PATH = os.path.join(settings.BASE_DIR, 'img1.jpg')  # Для option1
    BACKGROUND2_PATH = os.path.join(settings.BASE_DIR, 'img2.jpg')  # Для option2


    with tempfile.TemporaryDirectory() as temp_dir:
        for product_id in selected_ids:
            product = get_object_or_404(Product, id=product_id)
            print(product, product_id, product.main_photo)
            if not product.main_photo:
                continue
                
            option = request.POST.get(f'option_{product_id}', 'option1')
            BACKGROUND_IMAGE_PATH = BACKGROUND1_PATH if option == 'option1' else BACKGROUND2_PATH
            
            try:
                # Создаем композицию изображения
                with Image.open(BACKGROUND_IMAGE_PATH) as bg:
                    bg = bg.convert("RGBA")
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
                        
                        PX_TO_MM = 0.193023
                        def px_to_mm(px):
                            return px * PX_TO_MM
                        
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
                                        img = add_rounded_corners(img, radius=37)

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


                        #Вставка текста на картинку
                        if option == "option1":
                            #Вставка названия на картинку
                            # --- Подготовим прозрачный слой для текста ---
                            txt_layer = Image.new("RGBA", bg.size, (255, 255, 255, 0))
                            draw = ImageDraw.Draw(txt_layer)
                            font_size = 95
                            font_path = os.path.join(settings.BASE_DIR, 'static', 'Plumb.ttf')
                            font = ImageFont.truetype(font_path, font_size)  # Можно заменить на любой TTF-шрифт
                            # --- Положение текста ---
                            text_x, text_y = 2063, 508  # Координаты
                            draw.text((text_x, text_y), smart_wrap(product.name.upper()) , font=font, fill=(0, 0, 0, 255))    # Основной текст

                            bg = Image.alpha_composite(bg, txt_layer)

                        temp_img = os.path.join(temp_dir, f'comp_{product_id}.jpg')
                        bg.convert('RGB').save(temp_img, quality=95)
                
                # Добавляем страницу в PDF
                pdf.add_page()
               
                # Фоновое изображение (на всю страницу)
                pdf.image(temp_img, x=0, y=0, w=297, h=210)
                
                # Форматирование цены
                price_value = product.price
                price_str = f"{price_value:,.2f}".replace(',', ' ').replace('.', ',') + " руб."

                # Форматируем материалы и размеры с переносами строк
         
                materials_str = ','.join([m.name for m in product.materials.all()]).replace(',', '\n')
                dimensions_name_str = ','.join([d.name for d in product.dimensions.all()]).replace(',', '\n')
                dimensions_str = ','.join([d.size for d in product.dimensions.all()]).replace(',', '\n')

                # Различное позиционирование текста
                # Различное позиционирование текста
                if option == 'option1':
                    # Вариант 1: текст по центру
                    pdf.set_font('DejaVu', 'B', 18)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_xy(px_to_mm(190), px_to_mm(110))
                    pdf.cell(0, 0, price_str, align='L', ln=True)
                    pdf.set_text_color(0, 0, 0)
                    
                    pdf.set_font('DejaVu', '', 12)
                    # Материалы (левая колонка)
                    pdf.set_font('DejaVu', '', 12)
                    pdf.set_xy(px_to_mm(180), px_to_mm(150))
                    pdf.multi_cell(px_to_mm(100), px_to_mm(5), materials_str, align='L')

                    # Название материалов (правая колонка)
                    pdf.set_xy(px_to_mm(230), px_to_mm(150))
                    pdf.multi_cell(px_to_mm(100), px_to_mm(5), dimensions_name_str, align='L')
                    # Размеры (правая колонка)
                    pdf.set_font('DejaVu', 'B', 12)
                    pdf.set_xy(px_to_mm(250), px_to_mm(150))
                    pdf.multi_cell(px_to_mm(100), px_to_mm(5), dimensions_str, align='L')

                    # Описание
                    if product.description:
                        pdf.set_font('DejaVu', '', 14)
                        pdf.set_xy(px_to_mm(175), px_to_mm(50))
                        pdf.multi_cell(px_to_mm(287), px_to_mm(5), product.description, align='L')
                else:
                    # Вариант 2: текст слева
                    pdf.set_font('DejaVu', '', 18)
                    pdf.set_xy(px_to_mm(17), px_to_mm(40))
                    pdf.cell(px_to_mm(170), 0, product.name.upper(), ln=True)
                    
                    pdf.set_font('DejaVu', 'B', 18)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_xy(px_to_mm(35), px_to_mm(101))
                    pdf.cell(px_to_mm(200), px_to_mm(18), price_str, ln=True)
                    pdf.set_text_color(0, 0, 0)
                    
                    pdf.set_font('DejaVu', '', 12)

                    # Выводим материалы
                    pdf.set_font('DejaVu', '', 12)
                    pdf.set_xy(px_to_mm(23), px_to_mm(150))
                    pdf.multi_cell(px_to_mm(60), px_to_mm(5), materials_str, align='L')
                    
                    pdf.set_xy(px_to_mm(80), px_to_mm(150))
                    pdf.multi_cell(px_to_mm(100), px_to_mm(5), dimensions_name_str, align='L')
                    # Размеры
                    pdf.set_font('DejaVu', 'B', 12)
                    pdf.set_xy(px_to_mm(100), px_to_mm(150))
                    pdf.multi_cell(px_to_mm(60), px_to_mm(5), dimensions_str, align='L')

                    if product.description:
                        pdf.set_font('DejaVu', '', 14)
                        pdf.set_xy(px_to_mm(17), px_to_mm(50))
                        pdf.multi_cell(px_to_mm(170), px_to_mm(5), product.description, align='L')
                
                
                # Добавляем контактную информацию
                PHONE_NUMBER1 = "+7 (495) 191-27-18"
                PHONE_NUMBER2 = "+7 (962) 737-97-75"
                Y_CHOORDS = 195

                pdf.set_font('DejaVu', 'B', 18)
                pdf.set_text_color(0, 0, 0)

                pdf.set_xy(0, Y_CHOORDS)
                pdf.cell(75, 0, PHONE_NUMBER1, link=f"tel:{PHONE_NUMBER1}", align='C', ln=True)
                pdf.set_xy(220, Y_CHOORDS)
                pdf.cell(55, 0, PHONE_NUMBER2, link=f"tel:{PHONE_NUMBER2}", align='C', ln=True)

                pdf.set_font('DejaVu', '', 16)
                pdf.set_xy(90, Y_CHOORDS)
                pdf.cell(0, 0, "www.mebel-altezza.ru", ln=1, link="https://mebel-altezza.ru/")
                pdf.set_xy(160, Y_CHOORDS)
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
    products = Product.objects.prefetch_related('materials', 'dimensions').all()
    return render(request, 'offer/product_list.html', {'products': products})


def edit_product(request, product_id):
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
            
            # Обработка габаритов (ИСПРАВЛЕНО: добавлена обработка названий)
            dimensions_str = form.cleaned_data.get('dimensions_input', '')
            dimensions_name_str = form.cleaned_data.get('dimensions_name_input', '')
            
            # Создаем списки значений
            dimensions_list = [d.strip() for d in dimensions_str.split(',') if d.strip()]
            dimensions_name_list = [n.strip() for n in dimensions_name_str.split(',') if n.strip()]
            
            # Удаляем старые связи
            ProductDimensions.objects.filter(product=product).delete()
            
            # Создаем новые связи с учетом названий
            for i, dimension_size in enumerate(dimensions_list):
                # Берем название из списка, если есть, иначе пустая строка
                name = dimensions_name_list[i] if i < len(dimensions_name_list) else ''
                
                dimension, _ = Dimensions.objects.get_or_create(
                    size=dimension_size,
                    defaults={'name': name}  # Устанавливаем имя при создании
                )
                
                # Если объект уже существовал - обновляем имя
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
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        Product.objects.filter(id__in=product_ids).delete()
        return HttpResponse(status=200)
    return HttpResponse(status=400)

