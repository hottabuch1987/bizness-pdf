from django.contrib import admin
from .models import Product, Material, Dimensions, ProductMaterial, ProductDimensions

class ProductMaterialInline(admin.TabularInline):
    model = ProductMaterial
    extra = 1 

class ProductDimensionsInline(admin.TabularInline):
    model = ProductDimensions
    extra = 1 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('article', 'name', 'price', 'stock', 'color')
    search_fields = ('article', 'name')
    inlines = [ProductMaterialInline, ProductDimensionsInline]

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name',) 
    search_fields = ('name',)

@admin.register(Dimensions)
class DimensionsAdmin(admin.ModelAdmin):
    list_display = ('size', 'name')
    search_fields = ('size', 'name')

