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