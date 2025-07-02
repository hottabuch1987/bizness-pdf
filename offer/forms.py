from .models import Product
from django import forms


class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label='Выберите CSV файл', widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))


class ProductForm(forms.ModelForm):
    # Добавляем новые поля для ввода материалов и габаритов
    materials_input = forms.CharField(
        label="Материалы (через запятую)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    dimensions_input = forms.CharField(
        label="Габариты (через запятую)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    dimensions_name_input = forms.CharField(
        label="Название",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    


    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['materials', 'dimensions']  # Исключаем ManyToMany поля
        
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Материалы
            self.fields['materials_input'].initial = ', '.join(
                [m.name for m in self.instance.materials.all()]
            )
            
            # Габариты (размеры)
            dimensions_list = [
                d.size for d in self.instance.dimensions.all() 
                if d.size and d.size.strip()
            ]
            self.fields['dimensions_input'].initial = ', '.join(dimensions_list)
            
            # Названия габаритов (исправлено!)
            dimensions_name_list = [
                d.name for d in self.instance.dimensions.all()
                if d.name is not None  # Фильтруем None
            ]
            self.fields['dimensions_name_input'].initial = ', '.join(
                [name for name in dimensions_name_list if name]  # Фильтруем пустые строки
            )