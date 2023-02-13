import json
import time
import traceback

import requests
import scrapy
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


class GalleryScraperSpider(scrapy.Spider):
    name = "gallery_scraper"
    allowed_domains = ["www.bearspace.co.uk"]
    start_urls = ["http://www.bearspace.co.uk/"]

    # Use to export data:  scrapy crawl gallery_scraper -o scraped_data.csv

    def start_requests(self):
        """
        Function responsible for collecting raw data

        :return:
        """
        try:
            # Get cookie to use in API requests
            bearspace_cookies, auth_token = self._get_token_bearspace()
            url_to_request, bearspace_cookies_to_request, headers_to_request = self.get_request_information(
                bearspace_cookies=bearspace_cookies,
                auth_token=auth_token,
                current_page_number=0)
            # First request to know how many products have
            response_page = requests.get(url=url_to_request, cookies=bearspace_cookies_to_request,
                                         headers=headers_to_request)
            response_page = response_page.json()

            # Get maximum gallery items
            max_products_count = response_page['data']['catalog']['category']['productsWithMetaData']['totalCount']

            # 100 items per page
            maximum_pages = int(max_products_count / 100) + 1

            # Iterate through each page
            for i in range(maximum_pages):
                # Get necessary information to do requests
                url_to_request, bearspace_cookies_to_request, headers_to_request = self.get_request_information(
                    bearspace_cookies=bearspace_cookies,
                    auth_token=auth_token,
                    current_page_number=i)
                # Do request and send request information to parse function.
                yield scrapy.Request(url=url_to_request, callback=self.parse, cookies=bearspace_cookies_to_request,
                                     headers=headers_to_request)

        # Base exception because I test this script few times
        except BaseException:
            print(traceback.format_exc())
            time.sleep(45)

    def parse(self, response, **kwargs):
        """
        Parse data from requests

        :param response: Scrapy response request
        :param kwargs: kwargs
        :return: parsed data
        """
        response = json.loads(response.text)
        products_list = response['data']['catalog']['category']['productsWithMetaData']['list']

        for item in products_list:
            doc_item = {
                'url': str('https://www.bearspace.co.uk/product-page/' + str(item['urlPart'])),
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
        Gets cookies and authorization to be used in requests

        :return: cookies dict and authorization token
        """
        # I will use undetected chromedriver to bypass anti-bot systems.
        browser = uc.Chrome()

        # Let me explain the idea:
        """
        I analysed the website and I noticed that there's an API that give all information that we need. 
        But collecting information through this API is quite hard. 
        To access the API we have two requirements:
        1. Strong use of cookies. We need specially the "XSRF-TOKEN", "svSession" and "hs" credentials.
        2. Required use of server authorization. Without this, we will receive the 401 status code. 
        
        So, 
        1. To collect cookies, the initial use of selenium will be sufficient to get necessary cookies for future
        requests. 
        2. To get the authorization to use in requests headers, I noticed that the website makes a call to 
        https://www.bearspace.co.uk/_api/v2/dynamicmodel to just get the authentication to use in the next requests.
        The code authentication that we need is located for some reason in intId:1744. I don't know if eventually the 
        website changes this key, but from now is it.
        
        
        """
        browser.get('https://www.bearspace.co.uk/purchase?page=2')
        time.sleep(2)
        # Navigate to get more cookies
        browser.find_element(by=By.XPATH, value='//button[@class="txtqbB"]').click()
        time.sleep(2)
        # Get cookies from website
        cookies_collected = browser.get_cookies()
        browser.quit()
        # Create an unique cookie dict
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
        # Gets the authorization secret
        response = requests.get('https://www.bearspace.co.uk/_api/v2/dynamicmodel',
                                cookies=cookies_dict,
                                headers=headers)

        response = response.json()

        authorization_token = None
        # Find the authorization code that contains the key intId with 1744 value.
        for key, value in response["apps"].items():
            if value.get("intId") == 1744:
                authorization_token = value['instance']
                break

        return cookies_dict, authorization_token

    @staticmethod
    def get_request_information(bearspace_cookies, auth_token, current_page_number):
        """
        Just generates url, cookies and headers to future requests.

        :param bearspace_cookies: cookies that was collected in _get_token_bearspace function
        :param auth_token: Auth token that was given in _get_token_bearspace function
        :param current_page_number: current page number
        :return: edited_url, bearspace_cookies, headers
        """

        offset_number = int(current_page_number * 100)

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
        # Keep the original url to reference
        """original_url_api = 'https://www.bearspace.co.uk/_api/wix-ecommerce-storefront-web/api?o' \
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
                           '%3Afalse%7D'"""

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
                     '-000000000001%22%2C%22offset%22%3A' + str(offset_number) + \
                     '%2C%22limit%22%3A100%2C%22sort%22%3Anull' \
                     '%2C%22filters%22%3Anull%2C%22withOptions%22%3Afalse%2C%22withPriceRange%22' \
                     '%3Afalse%7D'

        return edited_url, bearspace_cookies, headers
