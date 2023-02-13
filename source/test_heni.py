import sys
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
        # self.second_challenge()
        #self.third_challenge()
        self.fourth_challenge()

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
        #####
        dim_df = pd.read_csv("assets/dim_df_correct.csv")

        for index, row in dim_df.iterrows():
            string_to_parse = str(row['rawDim'])

            result = extract_dimensions(string_to_parse=string_to_parse)
            print(string_to_parse, '>>>>', result)

    def third_challenge(self):
        from scrapy.crawler import CrawlerProcess
        from gallery_scraper_project.gallery_scraper_project.spiders.gallery_scraper import GalleryScraperSpider
        process = CrawlerProcess(settings={
            'FEEDS': {
                'collected_data.csv': {
                    'format': 'csv'
                }
            }
        }
        )

        process.crawl(GalleryScraperSpider)
        process.start()

    def fourth_challenge(self):
        flights = pd.read_csv("assets/flights.csv")
        airports = pd.read_csv("assets/airports.csv")
        weather = pd.read_csv("assets/weather.csv")
        airlines = pd.read_csv("assets/airlines.csv")

        """Inner join, Left join, Right join, and Full join are different types of SQL joins that combine two or more 
        tables based on a common column. These concepts are applicable to dataframes in Python as well.

        Inner join: An inner join returns only the rows that have matching values in both tables. The result set 
        contains only the rows that appear in both tables based on the join condition.

        Left join: A left join returns all the rows from the left table and the matching rows from the right table. 
        If there is no match, the result set will contain NULL values for the columns from the right table.

        Right join: A right join is similar to a left join, except that it returns all the rows from the right table 
        and the matching rows from the left table. If there is no match, the result set will contain NULL values for 
        the columns from the left table.

        Full join: A full join returns all the rows from both tables, whether there is a match or not. If there is no 
        match, the result set will contain NULL values for the columns from the missing table.
        
        
        """






def extract_dimensions(string_to_parse):
    # Expressão regular para o formato "19×52cm"
    match = re.match(r'(\d+(?:\.\d+)?)×(\d+(?:\.\d+)?)cm', string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), None

    # Expressão regular para o formato "50 x 66,4 cm"
    match = re.match(r"(\d+[.,]?\d+)[\sx]+([\d+[.,]?\d+)", string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), None

    # Expressão regular para o formato "168.9 x 274.3 x 3.8 cm (66 1/2 x 108 x 1 1/2 in.)"
    match = re.match(r'(\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) cm', string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), float(match.group(3))

    # Expressão regular para o formato "Sheet: 16 1/4 × 12 1/4 in. (41.3 × 31.1 cm) Image: 14 × 9 7/8 in. (35.6 × 25.1 cm)"
    match = re.search(r"Image:.*\((.*) × (.*) cm\)",
                      string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), None

    # Expressão regular para o formato "5 by 5in"
    match = re.match(r'(\d+(?:\.\d+)?) by (\d+(?:\.\d+)?)in', string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), None

    return None, None, None
