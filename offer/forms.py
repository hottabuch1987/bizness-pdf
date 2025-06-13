from .models import Product
from django import forms


class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label='Выберите CSV файл')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        
        widgets = {

            'main_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_photo1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_photo2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }