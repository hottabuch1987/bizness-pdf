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
  
    pdf.add_font('DejaVu', '', '/Users/hottabuch/PycharmProjects/business_offer/business/static/dejavu-fonts-ttf/ttf/DejaVuSansCondensed-Bold.ttf', uni=True)
    pdf.add_font


    background1_path = os.path.join(settings.BASE_DIR, 'img1.jpg')  # Для option1
    background2_path = os.path.join(settings.BASE_DIR, 'img2.jpg')  # Для option2
    
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
                    bg_width, bg_height = bg.size
                    
                    with Image.open(product.main_photo.path) as product_img:
                        # Обработка прозрачности
                        if product_img.mode == 'RGBA':
                            white_bg = Image.new('RGB', product_img.size, (255, 255, 255))
                            white_bg.paste(product_img, (0, 0), product_img)
                            product_img = white_bg
                        
                        # Различное позиционирование для разных вариантов
                        additional_photos = []
                        if option == "option1":
                            # Для option1: добавляем фото в нижнюю часть
                            if product.additional_photo1 and os.path.exists(product.additional_photo1.path):
                                additional_photos.append(product.additional_photo1.path)
                            if product.additional_photo2 and os.path.exists(product.additional_photo2.path):
                                additional_photos.append(product.additional_photo2.path)
                                
                            if additional_photos:
                                # Параметры для дополнительных фото
                                footer_height = int(bg_height * 0.22)  # 15% высоты
                                footer_y = bg_height - footer_height
                                total_width = bg_width
                                num_photos = len(additional_photos)
                                margin_x = 5  # Отступ по горизонтали
                                margin_y = 5   # Отступ по вертикали
                                
                                # Рассчет максимальной ширины для фото
                                max_photo_width = (total_width - (num_photos + 1) * margin_x) // num_photos
                                max_photo_height = footer_height - 2 * margin_y
                                
                                x_pos = margin_x
                                for photo_path in additional_photos:
                                    with Image.open(photo_path) as img:
                                        # Конвертация RGBA в RGB
                                        if img.mode == 'RGBA':
                                            white_bg = Image.new('RGB', img.size, (255, 255, 255))
                                            white_bg.paste(img, mask=img.split()[3])
                                            img = white_bg
                                        
                                        # Масштабирование с сохранением пропорций
                                        img.thumbnail((max_photo_width, max_photo_height), Image.LANCZOS)
                                        
                                        # Позиционирование
                                        y_pos = footer_y + margin_y + (max_photo_height - img.height) // 2
                                        bg.paste(img, (x_pos, y_pos))
                                        
                                        x_pos += img.width + margin_x
                        elif option == "option2":
                            # Для option2: добавляем фото слева от основного контента
                            additional_photos = []
                            if product.additional_photo1 and os.path.exists(product.additional_photo1.path):
                                additional_photos.append(product.additional_photo1.path)
                            if product.additional_photo2 and os.path.exists(product.additional_photo2.path):
                                additional_photos.append(product.additional_photo2.path)
                                
                            if additional_photos:
                                # Параметры для дополнительных фото
                                sidebar_width = int(bg_width * 0.3)  # 30% ширины
                                sidebar_x = int(bg_width * 0.6)     # 2% отступ слева
                                content_y = int(bg_height * 0.1)      # 10% отступ сверху
                                max_photo_height = int(bg_height * 0.32)  # 20% высоты
                                margin_y = 10  # Отступ между фото
                                
                                y_pos = content_y
                                for photo_path in additional_photos:
                                    with Image.open(photo_path) as img:
                                        # Конвертация RGBA в RGB
                                        if img.mode == 'RGBA':
                                            white_bg = Image.new('RGB', img.size, (255, 255, 255))
                                            white_bg.paste(img, mask=img.split()[3])
                                            img = white_bg
                                        
                                        # Масштабирование с сохранением пропорций
                                        img.thumbnail((sidebar_width, max_photo_height), Image.LANCZOS)
                                        
                                        # Позиционирование
                                        x_pos = sidebar_x + (sidebar_width - img.width) // 2
                                        bg.paste(img, (x_pos, y_pos))
                                        
                                        y_pos += img.height + margin_y
                    

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
                
                # Различное позиционирование текста для разных вариантов
                if option == 'option1':
                    # Вариант 1: текст по центру под изображением
                    # Заголовок
                    pdf.set_font('DejaVu', '', 12)
                    pdf.set_xy(50, 40)
                    pdf.cell(297, 15, product.name.upper(), align='C', ln=True)
                    
                    # Цена
                    pdf.set_font('DejaVu', '', 18)
                    pdf.set_text_color(220, 50, 50)  # Красный цвет
                    pdf.set_xy(80, 104)
                    pdf.cell(297, 20, price_str, align='C', ln=True)
                    pdf.set_text_color(0, 0, 0)  # Возврат к черному
                    
                    # Характеристики
                    pdf.set_font('DejaVu', '', 12)
                    
                    # # pdf.set_xy(50, 100)
                    # # pdf.cell(297, 10, f" {product.article}", align='C', ln=True)
                    
                    # pdf.set_xy(45, 150)
                    # # разбей по запятой
                    # material = product.material
                    
                    # pdf.cell(297, 10, f" {product.material}", align='C', ln=True)
                        # Разбиваем материалы по запятым и выводим каждую в отдельной строке
                    materials = product.material.split(',')
                    y_pos = 150  # Начальная позиция Y для материалов
                    
                    for material in materials:
                        material = material.strip()  # Убираем лишние пробелы
                        pdf.set_xy(45, y_pos)
                        pdf.cell(297, 10, material, align='C', ln=True)
                        y_pos += 8  # Отступ между строками
                    
                    pdf.set_xy(100, 150)
                    pdf.cell(297, 10, f" {product.dimensions}", align='C', ln=True)
                    
                    # pdf.set_xy(100, 180)
                    # pdf.cell(297, 10, f" {product.color}", align='C', ln=True)
                else:
                    # Вариант 2: текст слева
                    # Заголовок
                    pdf.set_font('DejaVu', '', 12)
                    pdf.set_xy(20, 40)
                    pdf.cell(150, 15, product.name.upper(), ln=True)
                    
                    # Цена
                    pdf.set_font('DejaVu', '', 18)
                    pdf.set_text_color(220, 50, 50)  # Красный цвет
                    pdf.set_xy(50, 108)
                    pdf.cell(150, 20, price_str, ln=True)
                    pdf.set_text_color(0, 0, 0)  # Возврат к черному
                    
                    # Характеристики
                    pdf.set_font('DejaVu', '', 12)
                    
                    # pdf.set_xy(30, info_y)
                    # pdf.cell(100, 10, f"{product.article}", ln=True)
                    
                    # pdf.set_xy(25, 100)
                    # pdf.cell(90, 130, f"{product.material}", ln=True)
                    # Разбиваем материалы по запятым и выводим каждую в отдельной строке
                    materials = product.material.split(',')
                    y_pos = 160  # Начальная позиция Y для материалов
                    
                    for material in materials:
                        material = material.strip()  # Убираем лишние пробелы
                        pdf.set_xy(17, y_pos)
                        pdf.cell(40, 0, material, align='C', ln=True)
                        y_pos += 8  # Отступ между строками
                    
                    pdf.set_xy(85,  150)
                    pdf.cell(297, 10, f"{product.dimensions}", ln=True)
                    
                    # pdf.set_xy(30, info_y + 30)
                    # pdf.cell(100, 10, f"{product.color}", ln=True)
                        
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



def simple_page(request):
    product = Product.objects.first()
   
    context = {
    'product': product
    }
    return render(request, 'offer/product.html', context)