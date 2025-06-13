"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from offer.views import upload_csv, product_list, edit_product, convert_to_pdf, simple_page, delete_products

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', upload_csv, name='upload_csv'),
    path('products/', product_list, name='product_list'),  
    path('edit/<int:product_id>/', edit_product, name='edit_product'),  
    path('delete-products/', delete_products, name='delete_products'),
    path('convert_to_pdf/', convert_to_pdf, name='convert_to_pdf'),
    path('product/', simple_page, name='simple_page'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)