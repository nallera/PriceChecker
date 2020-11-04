import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from searches.models import ProductModel, ProductSearchModel


class ProductSearch:

    def __init__(self, query, search_id, number):
        self._query = str(query).replace(" ", "-")
        self.search_id = search_id
        self.number = number

    @classmethod
    def create_from_product_search(cls, product_search):
        return cls(product_search.query, product_search.pk, product_search.number)

    def first_search(self):
        site = requests.get("https://listado.mercadolibre.com.ar/" + self._query)

        if site.status_code == 200:

            content = BeautifulSoup(site.content, 'html.parser')
            product_wrappers = content.find_all(class_='ui-search-result__content-wrapper')[0:self.number]
            image_wrappers = content.find_all(class_='ui-search-result__image')[0:self.number]

            products = self.scrape_wrappers(product_wrappers, image_wrappers)

            for product in products:
                prod_model = ProductModel(url=product.url,
                                          name=product.name,
                                          price=product.price,
                                          price_date=datetime.now(),
                                          img_url=product.img_url,
                                          previous_prices="{}",
                                          search=ProductSearchModel(pk=self.search_id))
                prod_model.save()

    def update(self):

        product_models = ProductModel.objects.filter(search_id=self.search_id)

        products = {single_product: Product.create_from_product(single_product)
                    for single_product in product_models}

        for product_model, product in products.items():

            site = requests.get(product.url)
            content = BeautifulSoup(site.content, 'html.parser')

            price_tags = content.find_all(class_="price-tag-fraction")
            new_price = float(str(price_tags[0].text).replace(".", ""))

            if product.price != new_price:
                previous_prices_dict = json.loads(product_model.previous_prices)
                if len(previous_prices_dict) == 0:
                    product_model.previous_prices = self.create_new_previous_prices(product.price, product.price_date)
                else:
                    product_model.previous_prices = self.add_new_previous_price(previous_prices_dict, product.price, product.price_date)

                product_model.price = new_price
                product_model.price_date = datetime.now()

                product_model.save()

    @staticmethod
    def create_new_previous_prices(previous_price, previous_price_date):
        return json.dumps({"price_values": [[str(previous_price_date), previous_price]]})

    @staticmethod
    def add_new_previous_price(previous_prices_dict, previous_price, previous_price_date):
        previous_prices_dict["price_values"].append([str(previous_price_date), previous_price])
        return json.dumps(previous_prices_dict)

    def scrape_wrappers(self, product_wrappers, image_wrappers):
        prices = [float(str(price_tag.text).replace(".", "")) for wrapper in product_wrappers
                  for price_tag in wrapper.find_all("span", class_="price-tag-fraction")]
        names = [name_tag.text for wrapper in product_wrappers
                 for name_tag in wrapper.find_all("h2", class_="ui-search-item__title")]
        urls = [url_tag.get('href').split("JM#")[0] + "JM" for wrapper in product_wrappers
                for url_tag in wrapper.find_all("a", class_="ui-search-item__group__element ui-search-link")]
        img_urls = [img_tag.get('data-src') for wrapper in image_wrappers
                    for img_tag in wrapper.find_all("img", class_="ui-search-result-image__element")]

        products = list(map(Product, names, urls, prices, [""]*self.number, img_urls, ["{}"]*self.number))
        return products


class Product:

    def __init__(self, name, url, price, price_date, img_url, previous_prices, prod_id=None):
        self.prod_id = prod_id or 0
        self.name = name
        self.url = url
        self.price = price
        self.price_date = price_date
        self.img_url = img_url
        self.previous_prices = previous_prices
        self.conversor = Conversor("https://www.dolarsi.com/api/api.php?type=valoresprincipales")

    def __str__(self):
        return f"Product {self.name}, priced at ${self.price}, url {self.url}, image {self.img_url}"

    @classmethod
    def create_from_product(cls, product):
        return cls(product.name, product.url, product.price, product.price_date,
                   product.img_url, product.previous_prices, product.pk)

    @property
    def price_oficial(self):
        return self.price/self.conversor.oficial

    @property
    def price_solidario(self):
        return self.price/self.conversor.solidario

    @property
    def price_blue(self):
        return self.price/self.conversor.blue


class Conversor:

    def __init__(self, url):
        self._url = url
        self.oficial = 1
        self.solidario = 1
        self.blue = 1
        self.get_exchange_rates()

    def get_exchange_rates(self):
        json_data = json.loads(str(requests.get(self._url).text))

        self.oficial = float(str(json_data[0]['casa']['venta']).replace(",", "."))
        self.solidario = self.oficial * 1.65
        self.blue = float(str(json_data[1]['casa']['venta']).replace(",", "."))