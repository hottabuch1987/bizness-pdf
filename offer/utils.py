import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings


# Функция для скругления углов
def add_rounded_corners(image, radius=37):
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


# Функция для обработки текста
def smart_wrap(text, max_width=21):
    lines = []
    current_line = ''

    for word in text.split():
        # Если слово длиннее, чем вся строка — переносим его отдельно
        if len(word) > max_width:
            if current_line:
                lines.append(current_line.rstrip())
                current_line = ''
            # Разбиваем очень длинное слово по max_width
            for i in range(0, len(word), max_width):
                lines.append(word[i:i+max_width])
            continue

        # Если слово помещается в текущую строку
        if len(current_line) + len(word) + 1 <= max_width:
            if current_line:
                current_line += ' ' + word
            else:
                current_line = word
        else:
            lines.append(current_line.rstrip())
            current_line = word

    if current_line:
        lines.append(current_line.rstrip())

    return '\n'.join(lines)


# Функция для обработки варианта option1
def process_option1(product, bg, font_path, resize_and_crop_cover, add_rounded_corners):
    """Обработка варианта option1"""
    # Основное изображение
    with Image.open(product.main_photo.path) as product_img:
        if product_img.mode != 'RGBA':
            product_img = product_img.convert('RGBA')
        
        target_width = 1118
        target_height = 2079
        position = (124, 125)
        
        product_img = resize_and_crop_cover(product_img, target_width, target_height)
        product_img = add_rounded_corners(product_img)
        bg.paste(product_img, position, product_img)

    # Дополнительные изображения
    additional_photos = []
    for photo_field in ['additional_photo1', 'additional_photo2']:
        photo = getattr(product, photo_field)
        if photo and os.path.exists(photo.path):
            additional_photos.append(photo.path)
    
    if additional_photos:
        photo_height = 1040
        photo_width = 604
        x_pos = 1309
        y_pos = 125

        for photo_path in additional_photos:
            with Image.open(photo_path) as img:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img = resize_and_crop_cover(img, photo_width, photo_height)
                img = add_rounded_corners(img, radius=37)
                bg.paste(img, (x_pos, y_pos), img)
                y_pos += photo_height

    # Добавление текста
    txt_layer = Image.new("RGBA", bg.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    font_size = 95
    font = ImageFont.truetype(font_path, font_size)
    text_x, text_y = 2063, 508
    draw.text((text_x, text_y), smart_wrap(product.name.upper()), font=font, fill=(0, 0, 0, 255))
    # Добавление описание
    text_x, text_y = 2063, 787
    font_description = ImageFont.truetype(font_path, 54)
    draw.text((text_x, text_y), smart_wrap(product.description, 50), font=font_description, fill=(0, 0, 0, 255))
    # Добавление цены
    text_x, text_y = 2229, 1257
    price_str = f"{product.price:.2f} руб."
    bold_font_path = os.path.join(settings.BASE_DIR, 'static', 'Plumb_bold.ttf')
    price_font_size = 87
    price_font = ImageFont.truetype(bold_font_path, price_font_size)
    draw.text((text_x, text_y), price_str, font=price_font, fill=(0, 0, 0, 255))
    # Добавление материалов

    start_x = 2063  # X-координата начала кружочков
    start_y = 1730  # Y-координата первого материала
    circle_radius = 20  # Радиус кружочков
    vertical_step = 58  # Расстояние между материалами
    text_offset = 28  # Отступ текста от кружочка
    
    # Получаем материалы продукта
    materials = product.materials.all()
    
    for i, material in enumerate(materials):
        # Текущая позиция Y
        current_y = start_y + i * vertical_step
        
        # Рисуем кружочек
        circle_center_x = start_x
        circle_center_y = current_y
        
        # Рассчитываем координаты ограничивающего прямоугольника
        x0 = circle_center_x - circle_radius
        y0 = circle_center_y - circle_radius
        x1 = circle_center_x + circle_radius
        y1 = circle_center_y + circle_radius
        
        fill_color = (0, 0, 0, 0)  # Белый по умолчанию
        

        font_size = 55
        # Рисуем кружочек
        draw.ellipse([(x0, y0), (x1, y1)], 
                    fill=fill_color, 
                    outline=(0, 0, 0, 255))  # Черная обводка
        
        # Выводим название материала
        text_x = start_x + circle_radius + text_offset
        text_y = current_y - font_size // 2  # Подстройка вертикального выравнивания
        
        # Преобразуем название материала в строку
        material_name = str(material.name) if material.name else ""
        font = ImageFont.truetype(font_path, font_size)
        draw.text((text_x, text_y), material_name, font=font, fill=(0, 0, 0, 255))

    # Название и размеры
 
    # Добавление размеров
    text_x, text_y = 2729, 1716
    dimensions = product.dimensions.all()
    dimensions_name_font_size = 55
    dimensions_size_font_size = 60
    
    # Создаем шрифты
    bold_font_path = os.path.join(settings.BASE_DIR, 'static', 'Plumb_bold.ttf')
    name_font = ImageFont.truetype(font_path, dimensions_name_font_size)  
    size_font = ImageFont.truetype(bold_font_path, dimensions_size_font_size)        
    
    # Вертикальный отступ между строками
    vertical_step = 58
    
    # Рисуем каждый размер
    for i, dim in enumerate(dimensions):
        current_y = text_y + i * vertical_step
        
        # Рисуем название размера (жирным)
        if dim.name:
            name_text = f"{dim.name}:"
            draw.text((text_x, current_y), name_text, font=name_font, fill=(0, 0, 0, 255))
            
            # Рассчитываем ширину названия для позиционирования значения
            name_width = draw.textlength(name_text, font=name_font)
        else:
            name_width = 0
        
        # Рисуем значение размера (обычным шрифтом)
        if dim.size:
            size_x = text_x + name_width + 20  # Добавляем небольшой отступ после двоеточия
            draw.text((size_x, current_y), dim.size, font=size_font, fill=(0, 0, 0, 255))

    return Image.alpha_composite(bg, txt_layer)


# Функция для обработки варианта option2
def process_option2(product, bg, font_path, resize_and_crop_cover, add_rounded_corners):
    """Обработка варианта option2"""
    # Основное изображение
    with Image.open(product.main_photo.path) as product_img:
        if product_img.mode != 'RGBA':
            product_img = product_img.convert('RGBA')
        
        target_width = 1970
        target_height = 1320
        position = (1395, 120)
        
        product_img = resize_and_crop_cover(product_img, target_width, target_height)
        product_img = add_rounded_corners(product_img)
        bg.paste(product_img, position, product_img)

    # Дополнительные изображения
    additional_photos = []
    for photo_field in ['additional_photo1', 'additional_photo2']:
        photo = getattr(product, photo_field)
        if photo and os.path.exists(photo.path):
            additional_photos.append(photo.path)
        
    if additional_photos:
        photo_height = 700
        photo_width = 700
        x_pos = 1970
        y_pos = 1500

        for photo_path in additional_photos:
            with Image.open(photo_path) as img:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img = resize_and_crop_cover(img, photo_width, photo_height)
                img = add_rounded_corners(img, radius=15)
                bg.paste(img, (x_pos, y_pos), img)
                x_pos += photo_width

    # Добавление текста
    txt_layer = Image.new("RGBA", bg.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    font_size = 95
    font = ImageFont.truetype(font_path, font_size)
    text_x, text_y = 207, 508
    draw.text((text_x, text_y), smart_wrap(product.name.upper()), font=font, fill=(0, 0, 0, 255))
    # Добавление описание
    text_x, text_y = 207, 787
    font_description = ImageFont.truetype(font_path, 54)
    draw.text((text_x, text_y), smart_wrap(product.description, 50), font=font_description, fill=(0, 0, 0, 255))
    # Добавление цены
    text_x, text_y = 373, 1257
    price_str = f"{product.price:.2f} руб."
    bold_font_path = os.path.join(settings.BASE_DIR, 'static', 'Plumb_bold.ttf')
    price_font_size = 87
    price_font = ImageFont.truetype(bold_font_path, price_font_size)
    draw.text((text_x, text_y), price_str, font=price_font, fill=(0, 0, 0, 255))
    # Добавление материалов

    start_x = 207  # X-координата начала кружочков
    start_y = 1730  # Y-координата первого материала
    circle_radius = 20  # Радиус кружочков
    vertical_step = 58  # Расстояние между материалами
    text_offset = 28  # Отступ текста от кружочка
    
    # Получаем материалы продукта
    materials = product.materials.all()
    
    for i, material in enumerate(materials):
        # Текущая позиция Y
        current_y = start_y + i * vertical_step
        
        # Рисуем кружочек
        circle_center_x = start_x
        circle_center_y = current_y
        
        # Рассчитываем координаты ограничивающего прямоугольника
        x0 = circle_center_x - circle_radius
        y0 = circle_center_y - circle_radius
        x1 = circle_center_x + circle_radius
        y1 = circle_center_y + circle_radius
        
        fill_color = (0, 0, 0, 0)  # Белый по умолчанию
        

        font_size = 55
        # Рисуем кружочек
        draw.ellipse([(x0, y0), (x1, y1)], 
                    fill=fill_color, 
                    outline=(0, 0, 0, 255))  # Черная обводка
        
        # Выводим название материала
        text_x = start_x + circle_radius + text_offset
        text_y = current_y - font_size // 2  # Подстройка вертикального выравнивания
        
        # Преобразуем название материала в строку
        material_name = str(material.name) if material.name else ""
        font = ImageFont.truetype(font_path, font_size)
        draw.text((text_x, text_y), material_name, font=font, fill=(0, 0, 0, 255))

    # Название и размеры
 
    # Добавление размеров
    text_x, text_y = 914, 1716
    dimensions = product.dimensions.all()
    dimensions_name_font_size = 55
    dimensions_size_font_size = 55
    
    # Создаем шрифты
    bold_font_path = os.path.join(settings.BASE_DIR, 'static', 'Plumb_bold.ttf')
    name_font = ImageFont.truetype(font_path, dimensions_name_font_size)  
    size_font = ImageFont.truetype(bold_font_path, dimensions_size_font_size)        
    
    # Вертикальный отступ между строками
    vertical_step = 58
    
    # Рисуем каждый размер
    for i, dim in enumerate(dimensions):
        current_y = text_y + i * vertical_step
        
        # Рисуем название размера (жирным)
        if dim.name:
            name_text = f"{dim.name}:"
            draw.text((text_x, current_y), name_text, font=name_font, fill=(0, 0, 0, 255))
            
            # Рассчитываем ширину названия для позиционирования значения
            name_width = draw.textlength(name_text, font=name_font)
        else:
            name_width = 0
        
        # Рисуем значение размера (обычным шрифтом)
        if dim.size:
            size_x = text_x + name_width + 20  # Добавляем небольшой отступ после двоеточия
            draw.text((size_x, current_y), dim.size, font=size_font, fill=(0, 0, 0, 255))

    return Image.alpha_composite(bg, txt_layer)


# Функция для добавления контактной информации
def add_contacts(pdf):
    """Добавление контактной информации на PDF"""
    PHONE_NUMBER1 = "+7 (495) 191-27-18"
    PHONE_NUMBER2 = "+7 (962) 737-97-75"
    Y_CHOORDS = 195

    pdf.set_font('DejaVu', 'B', 18)
    pdf.set_text_color(0, 0, 0)

    pdf.set_xy(0, Y_CHOORDS)
    pdf.cell(65, 0, PHONE_NUMBER1, link=f"tel:{PHONE_NUMBER1}", align='C', ln=True)
    pdf.set_xy(237, Y_CHOORDS)
    pdf.cell(55, 0, PHONE_NUMBER2, link=f"tel:{PHONE_NUMBER2}", align='C', ln=True)

    pdf.set_font('DejaVu', '', 16)
    pdf.set_xy(100, Y_CHOORDS)
    pdf.cell(0, 0, "www.mebel-altezza.ru", ln=1, link="https://mebel-altezza.ru/")
    pdf.set_xy(150, Y_CHOORDS)
    pdf.cell(0, 0, "info@mebel-altezza.ru", ln=1, link="mailto:info@mebel-altezza.ru")