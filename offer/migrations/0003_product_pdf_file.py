# Generated by Django 4.2.16 on 2025-06-09 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0002_remove_product_materials_remove_product_sizes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='product_pdfs/', verbose_name='PDF файл'),
        ),
    ]
