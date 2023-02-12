import time

from lxml import html
import re
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

import pandas as pd
import re


class HeniTrial:
    def __init__(self):
        print('')

    def start_test(self):
        print('initializing')
        # self.first_challenge()
        self.second_challenge()

    def first_challenge(self):
        print('first challenge')
        html_path = 'assets/webpage.html'

        with open(html_path, "r", encoding='utf-8') as f:
            html_file = f.read()

        soup = BeautifulSoup(html_file, 'html.parser')

        artist = soup.find('h1', {'class': 'lotName'}).text.split('(')[0].strip()
        print(artist)

        painting_name = soup.find('h2', {'class': 'itemName', 'id': 'main_center_0_lblLotSecondaryTitle'}).findNext(
            'i').text
        print(painting_name)

        price_estimated_gbp = soup.find("span", {"id": "main_center_0_lblPriceEstimatedPrimary"}).text
        print(price_estimated_gbp)

        price_realized_gbp = soup.find("span", {"id": "main_center_0_lblPriceRealizedPrimary"}).text
        print(price_realized_gbp)

        price_estimated_usd = soup.find("span", {"id": "main_center_0_lblPriceEstimatedSecondary"}).text
        print(price_estimated_usd)

        price_realized_usd = soup.find("div", {"id": "main_center_0_lblPriceRealizedSecondary"}).text
        print(price_realized_usd)

        image_url = soup.find("source", {"srcset": True})["srcset"]
        print(image_url)

        sale_date_str = soup.find("span", id="main_center_0_lblSaleDate").text.strip().rstrip(",")
        print(sale_date_str)
        sale_date = datetime.strptime(sale_date_str, '%d %B %Y').date()
        print(sale_date)

    def second_challenge(self):
        print('second')