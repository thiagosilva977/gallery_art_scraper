import json
import re
import time
import traceback

import requests
import scrapy
from bs4 import BeautifulSoup


class GalleryScraperSpider(scrapy.Spider):
    name = "gallery_scraper"
    allowed_domains = ["www.bearspace.co.uk"]
    start_urls = ["http://www.bearspace.co.uk/"]

    # Use to export data:  scrapy crawl gallery_scraper -o scraped_data.json

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

        except AttributeError:
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
            product_url = str('https://www.bearspace.co.uk/product-page/' + str(item['urlPart']))
            height = None
            width = None
            depth = None
            diameter = None
            product_year = None

            response = requests.get(product_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Getting full description
            og_description = soup.find('meta', {'property': 'og:description'})

            full_description = og_description['content']
            print(full_description)

            description = soup.find('pre', {'data-hook': 'description'})
            description_part = description.text

            p_tags = description.find_all('p')
            meta_info = None

            # iterate through p tags
            is_media_already_collected = False
            is_dimensions_collected = False
            is_year_collected = False
            for p in p_tags:

                # First tries to collect year of product.
                if is_year_collected:
                    pass
                else:
                    try:
                        regex_year = r'\b\d{4}\b'
                        match_year = re.search(regex_year, p.text)
                        if match_year:
                            product_year = int(match_year.group())
                            is_year_collected = True
                        else:
                            product_year = None

                    except AttributeError:
                        pass

                try:
                    if is_dimensions_collected:
                        pass
                    else:

                        # Try to parse "height 80.2cm x width 100cm" pattern.

                        current_string_0 = str(p.text).upper()
                        if 'WIDTH' in current_string_0 or 'HEIGHT' in current_string_0:
                            pattern = re.compile(
                                r'height\s*(\d+(\.\d+)?)\s*(cm)?\s*x\s*width\s*(\d+(\.\d+)?)\s*(cm)?')
                            match = pattern.search(p.text)
                            if match:
                                height = match.group(1)
                                width = match.group(4)
                                is_dimensions_collected = True
                                description_part = p.text

                        if is_dimensions_collected:
                            pass
                        else:
                            # Try to parse "58W x 85.5Hcm" pattern.

                            current_string_0 = str(p.text).upper()
                            if 'Hcm' in current_string_0:
                                pattern = re.compile(r'(\d+(\.\d+)?)\s*([wxWX])\s*(\d+(\.\d+)?)\s*([hH])?\s*(cm)?')
                                match = pattern.search(p.text)
                                if match:
                                    width = match.group(1)
                                    height = match.group(4)
                                    is_dimensions_collected = True
                                    description_part = p.text

                            if is_dimensions_collected:
                                pass
                            else:
                                # Try to parse "30cm diam" pattern.

                                current_string = p.text
                                current_string = current_string.replace('Hcm', 'cm').replace('Wcm', 'cm')
                                if 'DIAM' in str(current_string).upper():
                                    pattern = re.compile(r'(\d+\.?\d*)\s*(cm)?\s*diam')
                                    match = pattern.search(p.text)
                                    if match:
                                        diameter = match.group(1)
                                        is_dimensions_collected = True
                                        description_part = p.text
                                if is_dimensions_collected:
                                    pass
                                else:
                                    # Try to parse "height x width x depth" pattern but in some general way.

                                    if 'CM' in str(current_string).upper() or 'X' in str(current_string).upper():
                                        regex = r'(?P<height>\d+(?:\.\d+)?)(?:\s*x\s*(?P<width>\d+(?:\.\d+)?))?(' \
                                                r'?:\s*x\s*(?P<depth>\d+(?:\.\d+)?))?\s*(cm|CM)?'
                                        match_1 = re.search(regex, current_string)
                                        if match_1:
                                            height = match_1.group('height')
                                            width = match_1.group('width')
                                            if width is None:
                                                # Tries again to collect dimensions
                                                pattern = re.compile(
                                                    r'(\d+\.?\d*)\s*(cm)?\s*[xX]\s*(\d+\.?\d*)\s*(cm)?')
                                                match = pattern.search(current_string)
                                                if match:
                                                    width = match.group(3)
                                                else:
                                                    pattern = re.compile(
                                                        r'(\d+(\.\d+)?)\s*(cm)?\s*x\s*(\d+(\.\d+)?)\s*(cm)?')
                                                    match = pattern.search(p.text)
                                                    if match:
                                                        width = match.group(4)

                                            depth = match_1.group('depth')
                                            is_dimensions_collected = True
                                            description_part = p.text
                                        else:
                                            pass

                except AttributeError:
                    pass

                if is_media_already_collected:
                    pass
                else:
                    # Try to collect media
                    try:
                        # Try to collect "24k gold" pattern
                        pattern = re.compile(r'\d+[kK] gold')
                        if pattern.search(p.text):
                            meta_info = p.text
                            is_media_already_collected = True
                        else:
                            # Try to identify if the current p.text are dimensions type.
                            pattern = re.compile(r'(\d+(\.\d+)?)(cm)?\s*x\s*(\d+(\.\d+)?)(cm)?')
                            match = pattern.match(p.text)
                            if match:
                                pass
                            else:
                                # Try to identify if the current p.text are dimensions type again.

                                pattern = re.compile(r'\d+(\.\d+)?\s*[xX]\s*\d+(\.\d+)?\s*(cm)?')
                                if pattern.match(p.text):
                                    pass
                                else:
                                    # Try to avoid some strings
                                    current_text = str(p.text).upper()
                                    if 'ARTIST:' in current_text:
                                        pass
                                    elif 'SET OF ' in current_text:
                                        pass
                                    elif 'W X ' in current_text:
                                        pass
                                    elif 'Hcm' in current_text:
                                        pass
                                    elif 'CM:' in current_text:
                                        pass
                                    elif ' X :' in current_text:
                                        pass
                                    else:
                                        meta_info = p.text
                                        is_media_already_collected = True

                    except AttributeError:
                        pass

            # Additional regex to try to collect missing information
            if height is None and width is None and diameter is None:
                dimensions_regex = r'(\d+\.?\d*)\s*([wWxX])\s*(\d+\.?\d*)\s*([hH])\s*(c?m?)'
                padrao = re.compile(dimensions_regex)
                match = padrao.search(description_part)
                if match:
                    width = match.group(1)
                    height = match.group(3)
                else:
                    dimensions_regex2 = r'(\d+(\.\d+)?)(cm|cms)\s*x\s*(\d+(\.\d+)?)(cm|cms)'
                    match = re.search(dimensions_regex2, description_part)
                    if match:
                        width = float(match.group(1))
                        height = float(match.group(4))
                    else:
                        pattern3 = r"(\d+(?:\.\d+)?)(?:w|W)\s*x\s*(\d+(?:\.\d+)?)(?:h|H)\s*x\s*(\d+(?:\.\d+)?)(?:d|D)"
                        match = re.search(pattern3, description_part)
                        if match:
                            width, height, depth = match.groups()

            if width is not None:
                width = float(width)

            if height is not None:
                height = float(height)

            if depth is not None:
                depth = float(depth)

            if diameter is not None:
                diameter = float(diameter)

            if product_year is not None:
                product_year = int(product_year)

            doc_item = {
                'url': product_url,
                'image_url': str('https://static.wixstatic.com/media/' + str(item['media'][0]['url'])),
                'title': item['name'],
                'media': meta_info,
                'year': product_year,
                'height_cm': height,
                'width_cm': width,
                'depth_cm': depth,
                'diameter_cm': diameter,
                'price_gbp': item['price']
            }

            yield doc_item

    @staticmethod
    def _get_token_bearspace():
        """
        Gets cookies and authorization to be used in requests

        :return: cookies dict and authorization token
        """

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
        response = requests.get('https://www.bearspace.co.uk/purchase?page=2')

        cookies_dict = response.cookies.get_dict()

        # Create an unique cookie dict

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
        # Gets the authorization secret and svSession
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

        cookies_dict['svSession'] = response['svSession']

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
