# Generated by Django 4.2.16 on 2025-06-14 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0005_product_pdf_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='pdf_file',
        ),
    ]
