import json
import sys
import time
import traceback
import requests
import selenium
import scrapy
from bs4 import BeautifulSoup
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


class GalleryScraperSpider(scrapy.Spider):
    name = "gallery_scraper"
    allowed_domains = ["www.bearspace.co.uk"]
    start_urls = ["http://www.bearspace.co.uk/"]

    # Use to export data:  scrapy crawl gallery_scraper -o scraped_data.csv

    def start_requests(self):
        try:
            # Get cookie to use in API requests
            bearspace_cookies, auth_token = self._get_token_bearspace()
            edited_url, bearspace_cookies_new, headers = self.get_page_content(bearspace_cookies=bearspace_cookies,
                                                                               auth_token=auth_token,
                                                                               current_page=0)
            response_page = requests.get(url=edited_url, cookies=bearspace_cookies_new,
                                         headers=headers)
            response_page = response_page.json()

            max_products_count = response_page['data']['catalog']['category']['productsWithMetaData']['totalCount']

            maximum_pages = int(max_products_count / 100) + 1

            for i in range(maximum_pages):
                """response = requests.get(edited_url, cookies=bearspace_cookies,
                                                headers=headers,
                                                )"""

                edited_url, bearspace_cookies_new, headers = self.get_page_content(bearspace_cookies=bearspace_cookies,
                                                                                   auth_token=auth_token,
                                                                                   current_page=i)

                yield scrapy.Request(url=edited_url, callback=self.parse, cookies=bearspace_cookies_new,
                                     headers=headers)

                """response_page = self.get_page_content(bearspace_cookies=bearspace_cookies, auth_token=auth_token,
                                                      current_page=i)
                yield self.parse(response_page)"""
                """products_list = response_page['data']['catalog']['category']['productsWithMetaData']['list']
                print(len(products_list))
                for item in products_list:
                    yield self.parse(item)"""


        except:
            print(traceback.format_exc())
            time.sleep(45)

    def parse(self, response, **kwargs):
        response = json.loads(response.text)
        products_list = response['data']['catalog']['category']['productsWithMetaData']['list']

        for item in products_list:
            print(item)

            doc_item = {
                'url': str('https://www.bearspace.co.uk/product-page/'+str(item['urlPart'])),
                'title': item['name'],
                'media': item['customTextFields'],
                'height_cm': item['media'][0]['height'],
                'width_cm': item['media'][0]['width'],
                'price_gbp': item['price']
            }

            yield doc_item

    @staticmethod
    def _get_token_bearspace():
        """
        Gets cookies to be used in requests
        :return: cookies dict
        """
        browser = uc.Chrome()

        browser.get('https://www.bearspace.co.uk/purchase?page=2')
        time.sleep(2)
        browser.find_element(by=By.XPATH, value='//button[@class="txtqbB"]').click()
        time.sleep(2)
        cookies_collected = browser.get_cookies()
        browser.quit()
        cookies_dict = {}
        for cookie in cookies_collected:
            cookies_dict[cookie['name']] = cookie['value']

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.bearspace.co.uk/purchase?page=4',
            'Alt-Used': 'www.bearspace.co.uk',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

        response = requests.get('https://www.bearspace.co.uk/_api/v2/dynamicmodel',
                                cookies=cookies_dict,
                                headers=headers)

        response = response.json()

        authorization_token = None

        for key, value in response["apps"].items():
            if value.get("intId") == 1744:
                authorization_token = value['instance']
                break

        return cookies_dict, authorization_token

    def get_page_content(self, bearspace_cookies, auth_token, current_page):

        offset_number = int(current_page * 100)

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.bearspace.co.uk/_partials/wix-thunderbolt/dist/clientWorker.ac3e3c47.bundle.min.js',
            'Authorization': auth_token,
            'Content-Type': 'application/json; charset=utf-8',
            'X-XSRF-TOKEN': bearspace_cookies['XSRF-TOKEN'],
            'Alt-Used': 'www.bearspace.co.uk',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
        }

        original_url_api = 'https://www.bearspace.co.uk/_api/wix-ecommerce-storefront-web/api?o' \
                           '=getFilteredProducts&s=WixStoresWebClient&q=query,getFilteredProducts(' \
                           '$mainCollectionId:String!,$filters:ProductFilters,$sort:ProductSort,' \
                           '$offset:Int,$limit:Int,$withOptions:Boolean,=,false,$withPriceRange:Boolean,' \
                           '=,false){catalog{category(categoryId:$mainCollectionId){numOfProducts,' \
                           'productsWithMetaData(filters:$filters,limit:$limit,sort:$sort,offset:$offset,' \
                           'onlyVisible:true){totalCount,list{id,options{id,key,title,' \
                           '@include(if:$withOptions),optionType,@include(if:$withOptions),selections,' \
                           '@include(if:$withOptions){id,value,description,key,linkedMediaItems{url,' \
                           'fullUrl,thumbnailFullUrl:fullUrl(width:50,height:50),mediaType,width,height,' \
                           'index,title,videoFiles{url,width,height,format,quality}}}}productItems,' \
                           '@include(if:$withOptions){id,optionsSelections,price,formattedPrice,' \
                           'formattedComparePrice,availableForPreOrder,inventory{status,' \
                           'quantity}isVisible,pricePerUnit,formattedPricePerUnit}customTextFields(' \
                           'limit:1){title}productType,ribbon,price,comparePrice,sku,isInStock,urlPart,' \
                           'formattedComparePrice,formattedPrice,pricePerUnit,formattedPricePerUnit,' \
                           'pricePerUnitData{baseQuantity,baseMeasurementUnit}itemDiscount{' \
                           'discountRuleName,priceAfterDiscount}digitalProductFileItems{fileType}name,' \
                           'media{url,index,width,mediaType,altText,title,height}isManageProductItems,' \
                           'productItemsPreOrderAvailability,isTrackingInventory,inventory{status,' \
                           'quantity,availableForPreOrder,preOrderInfoView{limit}}subscriptionPlans{list{' \
                           'id,visible}}priceRange(withSubscriptionPriceRange:true),' \
                           '@include(if:$withPriceRange){fromPriceFormatted}discount{mode,' \
                           'value}}}}}}&v=%7B%22mainCollectionId%22%3A%2200000000-000000-000000' \
                           '-000000000001%22%2C%22offset%22%3A20%2C%22limit%22%3A20%2C%22sort%22%3Anull' \
                           '%2C%22filters%22%3Anull%2C%22withOptions%22%3Afalse%2C%22withPriceRange%22' \
                           '%3Afalse%7D'

        # Increased request data items from 20 to 100
        edited_url = 'https://www.bearspace.co.uk/_api/wix-ecommerce-storefront-web/api?o' \
                     '=getFilteredProducts&s=WixStoresWebClient&q=query,getFilteredProducts(' \
                     '$mainCollectionId:String!,$filters:ProductFilters,$sort:ProductSort,' \
                     '$offset:Int,$limit:Int,$withOptions:Boolean,=,false,$withPriceRange:Boolean,' \
                     '=,false){catalog{category(categoryId:$mainCollectionId){numOfProducts,' \
                     'productsWithMetaData(filters:$filters,limit:$limit,sort:$sort,offset:$offset,' \
                     'onlyVisible:true){totalCount,list{id,options{id,key,title,' \
                     '@include(if:$withOptions),optionType,@include(if:$withOptions),selections,' \
                     '@include(if:$withOptions){id,value,description,key,linkedMediaItems{url,' \
                     'fullUrl,thumbnailFullUrl:fullUrl(width:50,height:50),mediaType,width,height,' \
                     'index,title,videoFiles{url,width,height,format,quality}}}}productItems,' \
                     '@include(if:$withOptions){id,optionsSelections,price,formattedPrice,' \
                     'formattedComparePrice,availableForPreOrder,inventory{status,' \
                     'quantity}isVisible,pricePerUnit,formattedPricePerUnit}customTextFields(' \
                     'limit:1){title}productType,ribbon,price,comparePrice,sku,isInStock,urlPart,' \
                     'formattedComparePrice,formattedPrice,pricePerUnit,formattedPricePerUnit,' \
                     'pricePerUnitData{baseQuantity,baseMeasurementUnit}itemDiscount{' \
                     'discountRuleName,priceAfterDiscount}digitalProductFileItems{fileType}name,' \
                     'media{url,index,width,mediaType,altText,title,height}isManageProductItems,' \
                     'productItemsPreOrderAvailability,isTrackingInventory,inventory{status,' \
                     'quantity,availableForPreOrder,preOrderInfoView{limit}}subscriptionPlans{list{' \
                     'id,visible}}priceRange(withSubscriptionPriceRange:true),' \
                     '@include(if:$withPriceRange){fromPriceFormatted}discount{mode,' \
                     'value}}}}}}&v=%7B%22mainCollectionId%22%3A%2200000000-000000-000000' \
                     '-000000000001%22%2C%22offset%22%3A' + str(
            offset_number) + '%2C%22limit%22%3A100%2C%22sort%22%3Anull' \
                             '%2C%22filters%22%3Anull%2C%22withOptions%22%3Afalse%2C%22withPriceRange%22' \
                             '%3Afalse%7D'

        """response = requests.get(edited_url, cookies=bearspace_cookies,
                                headers=headers,
                                )"""

        return edited_url, bearspace_cookies, headers
