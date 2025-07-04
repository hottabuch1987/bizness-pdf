from .models import Product, Material, Dimension
from django import forms
from django.forms import inlineformset_factory


class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label='Выберите CSV файл', widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'
    
        
        widgets = {
            'main_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_photo1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_photo2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'article': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            
        }

MaterialFormSet = inlineformset_factory(
    Product,
    Material,
    fields=('name',),
    extra=1,
    can_delete=True,
    widgets={'name': forms.TextInput(attrs={'class': 'form-control'})}
)

DimensionFormSet = inlineformset_factory(
    Product,
    Dimension,
    fields=('name', 'value',),
    extra=1,
    can_delete=True,
    widgets={
        'name': forms.TextInput(attrs={'class': 'form-control'}),
        'value': forms.TextInput(attrs={'class': 'form-control'})
    }
)

