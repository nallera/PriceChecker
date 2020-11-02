import json
import requests
from bs4 import BeautifulSoup


class Product:

    def __init__(self, url, name=None, price=None):
        self.url = url
        self._name = name or ""
        self.price = price or 0

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if not isinstance(value, str):
            raise TypeError(f"The URL ({value}) must be a string, but it's a {type(value)}")
        elif value.startswith("http://") or value.startswith("https://"):
            self._url = value
        else:
            raise ValueError("An incorrect url was use to create the product object")

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        try:
            price_aux = float(value)
        except ValueError:
            raise ValueError("The price can only be a number")

        if price_aux >= 0:
            self._price = price_aux
        else:
            raise ValueError("Price must be a positive value")

    def scrape(self):
        site = requests.get(self.url)

        if site.status_code != 200:
            print(f"Error connecting to {self.url}")
        else:
            content = BeautifulSoup(site.content, 'html.parser')

            price_section = content.find_all(class_='price-tag ui-pdp-price__part')
            self.price = float(price_section[0].meta.get("content"))

            name_section = content.find_all(class_='ui-pdp-title')
            self._name = name_section[0].text

    def __str__(self):
        return f"Product {self._name}, priced at ${self._price}"


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


class SearchProduct:

    def __init__(self, query):
        self._query = str(query).replace(" ", "-")
        self.products = []
        self.conversor = Conversor("https://www.dolarsi.com/api/api.php?type=valoresprincipales")

    @property
    def mean_price(self):
        return sum([prod.price for prod in self.products])/len(self.products)

    def update(self):
        site = requests.get("https://listado.mercadolibre.com.ar/" + self._query)

        if site.status_code != 200:
            print(f"Error connecting to https://listado.mercadolibre.com.ar/{self._query}")
        else:
            content = BeautifulSoup(site.content, 'html.parser')
            product_wrappers = content.find_all(class_='ui-search-result__content-wrapper')[0:5]

            products = self.scrape_wrappers(product_wrappers)

            for product in products:
                self.products.append(product)

    @staticmethod
    def scrape_wrappers(product_wrappers):
        prices = [float(str(price_tag.text).replace(".", "")) for wrapper in product_wrappers
                  for price_tag in wrapper.find_all("span", class_="price-tag-fraction")]
        names = [name_tag.text for wrapper in product_wrappers
                 for name_tag in wrapper.find_all("h2", class_="ui-search-item__title")]
        urls = [url_tag.get('href').split("JM#")[0] + "JM" for wrapper in product_wrappers
                for url_tag in wrapper.find_all("a", class_="ui-search-item__group__element ui-search-link")]

        products = list(map(Product, urls, names, prices))
        return products

    def __str__(self):
        if len(self.products) == 0:
            return "There are no results for that query"

        result = f"Search for \"{self._query.replace('-',' ')}\" top {len(self.products)} results:\n"

        for product in self.products:
            result += f"{product} (USD{product.price/self.conversor.oficial:.2f}, " \
                      f"solidUSD{product.price/self.conversor.solidario:.2f}, " \
                      f"BUSD{product.price/self.conversor.blue:.2f})\n"

        result += f"Mean price is ${self.mean_price}"

        result += f" (USD{self.mean_price / self.conversor.oficial:.2f}, " \
                  f"solidUSD{self.mean_price / self.conversor.solidario:.2f}, " \
                  f"BUSD{self.mean_price / self.conversor.blue:.2f})\n"

        return result
