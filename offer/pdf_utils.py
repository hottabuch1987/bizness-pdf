# from io import BytesIO
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT
# from django.core.files.base import ContentFile

# def generate_product_pdf(product):
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=A4)
#     styles = getSampleStyleSheet()
    
#     # Кастомные стили
#     title_style = ParagraphStyle(
#         'Title',
#         parent=styles['Heading1'],
#         fontSize=18,
#         alignment=TA_CENTER,
#         textColor=colors.darkblue,
#         spaceAfter=20
#     )
    
#     price_style = ParagraphStyle(
#         'Price',
#         parent=styles['Heading2'],
#         fontSize=16,
#         textColor=colors.red,
#         spaceAfter=15
#     )
    
#     section_style = ParagraphStyle(
#         'Section',
#         parent=styles['Heading3'],
#         fontSize=14,
#         textColor=colors.darkgreen,
#         spaceAfter=10
#     )
    
#     # Элементы PDF
#     elements = []
    
#     # Заголовок
#     elements.append(Paragraph(f" {product.name}", title_style))
#     elements.append(Spacer(1, 20))
    
#     # Цена
#     price_text = f"<b>ЦЕНА:</b> {float(product.price):,.2f} руб.".replace(',', ' ')
#     elements.append(Paragraph(price_text, price_style))
#     elements.append(Spacer(1, 25))
    
#     # Материалы
#     elements.append(Paragraph("<b>МАТЕРИАЛЫ:</b>", section_style))
#     for m in product.material.split('\n'):
#         if m.strip():
#             elements.append(Paragraph(f"• {m.strip()}", styles['Normal']))
#     elements.append(Spacer(1, 15))
    
    
    
#     # Генерация PDF
#     doc.build(elements)
#     buffer.seek(0)
#     return buffer


from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from io import BytesIO


def generate_pdf(self):
    context = {
        'product': self,
        'price_formatted': f"{self.price:,.2f} руб.".replace(',', ' '),
    }
    
    html_string = render_to_string('admin/product_template.html', context)
    
    # Проверка HTML перед генерацией PDF
    with open('debug.html', 'w', encoding='utf-8') as f:
        f.write(html_string)
    
    buffer = BytesIO()
    pdf = pisa.CreatePDF(html_string, dest=buffer, encoding='utf-8')  # Явно указываем кодировку
    
    if pdf.err:
        print("Ошибка генерации PDF:", pdf.err)  # Логируем ошибку
        return None
    
    self.pdf_file.save(f'product_{self.article}.pdf', ContentFile(buffer.getvalue()))
    self.save()
    return self.pdf_file