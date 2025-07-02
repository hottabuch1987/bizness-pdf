from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.core.files import File
from io import TextIOWrapper
import csv

from .models import Product, Material, Dimensions, ProductMaterial, ProductDimensions

class ProductMaterialInline(admin.TabularInline):
    model = ProductMaterial
    extra = 1  # Количество пустых форм для добавления новых материалов

class ProductDimensionsInline(admin.TabularInline):
    model = ProductDimensions
    extra = 1  # Количество пустых форм для добавления новых размеров

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('article', 'name', 'price', 'stock', 'color')  # Поля, отображаемые в списке
    search_fields = ('article', 'name')  # Поля для поиска
    inlines = [ProductMaterialInline, ProductDimensionsInline]  # Встраиваемые формы для материалов и размеров

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Поля, отображаемые в списке
    search_fields = ('name',)  # Поля для поиска

@admin.register(Dimensions)
class DimensionsAdmin(admin.ModelAdmin):
    list_display = ('size', 'name')  # Поля, отображаемые в списке
    search_fields = ('size', 'name')  # Поля для поиска

