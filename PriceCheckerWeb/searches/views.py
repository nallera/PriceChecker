from django.forms import modelform_factory
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from searches.models import ProductSearchModel, ProductModel
from searches.meli import Product, ProductSearch


def all_searches(request):
    searches = ProductSearchModel.objects.all()
    return render(request, 'searches/all_searches.html', {"searches": searches})


def search(request, search_id):
    particular_search = get_object_or_404(ProductSearchModel, pk=search_id)
    product_models = ProductModel.objects.filter(search=search_id)
    products = [Product.create_from_product(single_product) for single_product in product_models]

    return render(request, 'searches/detail_search.html',
                  {'particular_search': particular_search,
                   'products': products,
                   'product_count': len(products)})


def product(request, prod_id):
    particular_product = get_object_or_404(ProductModel, pk=prod_id)
    return render(request, 'searches/detail_search.html', {'products': particular_product})


def update_prices(request, search_id):
    search_model = get_object_or_404(ProductSearchModel, pk=search_id)
    search = ProductSearch(search_model.query, search_model.pk, search_model.number)
    search.update()
    return redirect('search', search_id=search_id)


ProductSearchForm = modelform_factory(ProductSearchModel, exclude=[])


def new_search(request):
    if request.method == "POST":
        submitted_form = ProductSearchForm(request.POST)
        if submitted_form.is_valid():
            saved_search_model = submitted_form.save()
            saved_search = ProductSearch.create_from_product_search(saved_search_model)
            return redirect('search', search_id=saved_search.search_id)
        else:
            return render(request, "searches/new_search.html", {"form": submitted_form})
    else:
        form = ProductSearchForm()
        return render(request, "searches/new_search.html", {"form": form})


def delete_search(request, search_id):
    ProductSearchModel.objects.get(pk=search_id).delete()
    return redirect('all_searches')
