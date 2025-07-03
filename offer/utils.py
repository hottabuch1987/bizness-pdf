from PIL import Image, ImageDraw

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

