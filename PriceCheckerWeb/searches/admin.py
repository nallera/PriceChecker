from django.contrib import admin

from searches.models import ProductModel, ProductSearchModel

admin.site.register(ProductSearchModel)
admin.site.register(ProductModel)
