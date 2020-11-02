from meli import Product, SearchProduct
import requests
from bs4 import BeautifulSoup

if __name__ == '__main__':
    
    # products_to_check = [Product("https://articulo.mercadolibre.com.ar/MLA-814014095-korg-minilogue-xd-"
    #                              "sintetizador-analogico-polifonico-oddity-_JM "),
    #                      Product("https://articulo.mercadolibre.com.ar/MLA-858173538-interface-de-audio-"
    #                              "audient-evo-4-_JM")]
    #
    # for product in products_to_check:
    #     product.scrape()
    #     print(product)

    while True:
        search = SearchProduct(input("Enter what you need to check in Mercado Libre:"))
        search.update()
        print(search)
