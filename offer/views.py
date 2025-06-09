from django.shortcuts import render
from .models import Product

def simple_page(request):
    product = Product.objects.first()
    print(product.main_photo) 
    context = {
    'product': product
    }

    return render(request, 'admin/product_template.html', context)