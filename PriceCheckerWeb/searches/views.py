import json
from bokeh.models import DatetimeTickFormatter
from django.forms import modelform_factory
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from searches.models import ProductSearchModel, ProductModel
from searches.meli import Product, ProductSearch
from bokeh.plotting import figure
from bokeh.embed import components
import bokeh.palettes as pltts
import pandas as pd
import numpy as np
import datetime


def all_searches(request):
    searches = ProductSearchModel.objects.all()
    return render(request, 'searches/all_searches.html', {"searches": searches})


def search(request, search_id):
    particular_search = get_object_or_404(ProductSearchModel, pk=search_id)
    product_models = ProductModel.objects.filter(search=search_id)
    products = [Product.create_from_product(single_product) for single_product in product_models]

    fig = figure(x_axis_type='datetime',
                 x_axis_label='Date',
                 y_axis_label='Price',
                 plot_width=800,
                 plot_height=400)
    fig.xaxis.major_label_orientation = 3.1415 / 2
    fig.xaxis.formatter = DatetimeTickFormatter(
        hours=["%m/%d %H:%M"],
        days=["%m/%d %H:%M"],
        months=["%m/%d %H:%M"],
        years=["%m/%d %H:%M"],
    )

    palette = pltts.brewer['Set2'][len(products)]

    for pal_index, product in enumerate(products):
        prices = json.loads(product.previous_prices)['price_values']
        dates_str = json.loads(product.previous_prices)['date_values']
        dates = []
        for d in dates_str:
            d = d.split('.')[0]
            dates.append(datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S'))

        fig.step(x=dates, y=prices, color=palette[pal_index], legend_label=product.name.split(' ')[0]+str(pal_index), mode="after")
        fig.circle(x=dates, y=prices, color=palette[pal_index], fill_color="white", size=8)

    script, div = components(fig)

    return render(request, 'searches/detail_search.html',
                  {'particular_search': particular_search,
                   'products': products,
                   'product_count': len(products),
                   'script': script,
                   'div': div})


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
            saved_search.first_search()
            return redirect('search', search_id=saved_search.search_id)
        else:
            return render(request, "searches/new_search.html", {"form": submitted_form})
    else:
        form = ProductSearchForm()
        return render(request, "searches/new_search.html", {"form": form})


def delete_search(request, search_id):
    ProductSearchModel.objects.get(pk=search_id).delete()
    return redirect('all_searches')
