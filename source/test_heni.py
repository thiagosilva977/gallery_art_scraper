import re
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup


class HeniTrial:
    def __init__(self):
        print('')

    def start_test(self):
        print('initializing tasks:')
        self.first_challenge()
        time.sleep(2)
        self.second_challenge()
        time.sleep(2)
        self.third_challenge()
        time.sleep(2)
        self.fourth_challenge()

    @staticmethod
    def first_challenge():
        """
        Task 1: Parsing HTML
        :return:
        """
        html_path = 'assets/webpage.html'

        with open(html_path, "r", encoding='utf-8') as f:
            html_file = f.read()

        soup = BeautifulSoup(html_file, 'html.parser')

        artist = soup.find('h1', {'class': 'lotName'}).text.split('(')[0].strip()
        # print(artist)

        painting_name = soup.find('h2', {'class': 'itemName', 'id': 'main_center_0_lblLotSecondaryTitle'}).findNext(
            'i').text
        # print(painting_name)

        price_estimated_gbp = soup.find("span", {"id": "main_center_0_lblPriceEstimatedPrimary"}).text
        # print(price_estimated_gbp)

        price_realized_gbp = soup.find("span", {"id": "main_center_0_lblPriceRealizedPrimary"}).text
        # print(price_realized_gbp)

        price_estimated_usd = soup.find("span", {"id": "main_center_0_lblPriceEstimatedSecondary"}).text
        # print(price_estimated_usd)

        price_realized_usd = soup.find("div", {"id": "main_center_0_lblPriceRealizedSecondary"}).text
        # print(price_realized_usd)

        image_url = soup.find("source", {"srcset": True})["srcset"]
        # print(image_url)

        sale_date_str = soup.find("span", id="main_center_0_lblSaleDate").text.strip().rstrip(",")
        # print(sale_date_str)
        sale_date = datetime.strptime(sale_date_str, '%d %B %Y').date()
        # print(sale_date)

        parsed_data = {
            'artist_name': artist,
            'painting_name': painting_name,
            'price_realised_gbp': price_realized_gbp,
            'price_realised_usd': price_realized_usd,
            'price_estimated_gbp': price_estimated_gbp,
            'price_estimated_usd': price_estimated_usd,
            'url_painting_image': image_url,
            'saledate_paiting': sale_date
        }

        df = pd.DataFrame([parsed_data])

        print('\n\nHTML parsed task: ')
        print(df)
        print('----------------------------\n\n')

    @staticmethod
    def second_challenge():
        """
        Task 2: Regex
        :return:
        """
        dim_df = pd.read_csv("assets/dim_df_correct.csv")
        new_data_results = []
        for index, row in dim_df.iterrows():
            string_to_parse = str(row['rawDim'])

            result = extract_dimensions(string_to_parse=string_to_parse)
            # print(string_to_parse, '>>>>', result)

            new_data = {
                'rawDim': string_to_parse,
                'height': result[0],
                'width': result[1],
                'depth': result[2]
            }
            new_data_results.append(new_data)

        df = pd.DataFrame(new_data_results)
        print('\n\nNew data parsed with regex: ')
        print(df)
        print('----------------------------\n\n')

    @staticmethod
    def third_challenge():
        """
        Task 3: Web scraper
        :return:
        """
        from scrapy.crawler import CrawlerProcess
        from gallery_scraper_project.gallery_scraper_project.spiders.gallery_scraper import GalleryScraperSpider
        process = CrawlerProcess(settings={
            'FEEDS': {
                'collected_data.xlsx': {
                    'format': 'xlsx'
                }
            }
        }
        )

        process.crawl(GalleryScraperSpider)
        process.start()
        print('\n\nTask 3 - Check the collected_data.csv file. \n\n')

    @staticmethod
    def fourth_challenge():
        """
        Task 4: Data (SQL)

        :return:
        """
        # flights = pd.read_csv("assets/flights.csv")
        # airports = pd.read_csv("assets/airports.csv")
        # weather = pd.read_csv("assets/weather.csv")
        # airlines = pd.read_csv("assets/airlines.csv")

        # print(flights)
        # print(airlines)
        # print(airports)
        # print(weather)

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
        print('\n\nFourth task:\n\n')

        mystring = """
        Using MYSQL to do the sql commands: 
        
        1. Add full airline name to the flights dataframe and show the arr_time, origin, dest and the name of the 
        airline.
        
        SELECT flights.arr_time, flights.origin, flights.dest, airlines.name
        FROM flights
        JOIN airlines ON flights.carrier = airlines.carrier;
    
        2. Filter resulting data.frame to include only flights containing the word JetBlue
        
        SELECT flights.arr_time, flights.origin, flights.dest, airlines.name
        FROM flights
        JOIN airlines ON flights.carrier = airlines.carrier
        WHERE airlines.name LIKE '%JetBlue%';
    
        
        3. Summarise the total number of flights by origin in ascending.
    
        SELECT flights.origin, COUNT(flights.origin) AS total_flights
        FROM flights
        GROUP BY flights.origin
        ORDER BY total_flights ASC;
        
        4. Filter resulting data.frame to return only origins with more than 100 flights.
        
        SELECT flights.origin, COUNT(flights.origin) AS total_flights
        FROM flights
        GROUP BY flights.origin
        HAVING total_flights > 100
        ORDER BY total_flights ASC;
    
        
        """

        print(mystring)


def extract_dimensions(string_to_parse):
    # Regex to "19×52cm"
    match = re.match(r'(\d+(?:\.\d+)?)×(\d+(?:\.\d+)?)cm', string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), None

    # Regex to "50 x 66,4 cm"
    match = re.match(r"(\d+[.,]?\d+)[\sx]+([\d+[.,]?\d+)", string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), None

    # Regex to "168.9 x 274.3 x 3.8 cm (66 1/2 x 108 x 1 1/2 in.)"
    match = re.match(r'(\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) cm', string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), float(match.group(3))

    # Regex to "Sheet: 16 1/4 × 12 1/4 in. (41.3 × 31.1 cm) Image: 14 × 9 7/8 in. (35.6 × 25.1 cm)"
    match = re.search(r"Image:.*\((.*) × (.*) cm\)",
                      string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), None

    # Regex to "5 by 5in"
    match = re.match(r'(\d+(?:\.\d+)?) by (\d+(?:\.\d+)?)in', string_to_parse)
    if match:
        return float(match.group(1)), float(match.group(2)), None

    return None, None, None
