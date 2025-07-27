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
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля обязательными только при создании нового товара
        if not self.instance.pk:
            self.fields['main_photo'].required = True
            self.fields['additional_photo1'].required = True
            self.fields['additional_photo2'].required = True

    def clean(self):
        cleaned_data = super().clean()
        # Для существующих товаров проверяем, что фото либо уже есть, либо загружены новые
        if self.instance.pk:
            main_photo = cleaned_data.get('main_photo')
            additional_photo1 = cleaned_data.get('additional_photo1')
            additional_photo2 = cleaned_data.get('additional_photo2')
            
            if not main_photo and not self.instance.main_photo:
                self.add_error('main_photo', "Основное изображение обязательно")
            if not additional_photo1 and not self.instance.additional_photo1:
                self.add_error('additional_photo1', "Дополнительное изображение 1 обязательно")
            if not additional_photo2 and not self.instance.additional_photo2:
                self.add_error('additional_photo2', "Дополнительное изображение 2 обязательно")
        
        return cleaned_data

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

