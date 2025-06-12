from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.core.files import File
from io import TextIOWrapper
import csv

from .models import Product

admin.site.register(Product)