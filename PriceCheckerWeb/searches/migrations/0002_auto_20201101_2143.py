# Generated by Django 3.1.2 on 2020-11-02 00:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('searches', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product',
            new_name='ProductModel',
        ),
        migrations.RenameModel(
            old_name='ProductSearch',
            new_name='ProductSearchModel',
        ),
    ]
