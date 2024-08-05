from pathlib import Path
from typing import Iterable
from sheriff_scraper.items import SheriffScraperItem

import requests


import scrapy
from scrapy_playwright.page import PageMethod

import usaddress


class SheriffSpider(scrapy.Spider):
    name = "cuyahoga"
    allowed_domains = ['cuyahoga.sheriffsaleauction.ohio.gov', 'nominatim.openstreetmap.org']
    max_retries = 3

    def errback(self, failure):
        self.logger.error(repr(failure))
        if failure.check(scrapy.spidermiddlewares.httperror.HttpError):
            response = failure.value.response
            self.logger.error(f'HttpError on {response.url}')
        elif failure.check(scrapy.core.downloader.handlers.http11.TunnelError):
            request = failure.request
            self.logger.error(f'TunnelError on {request.url}')
        elif failure.check(scrapy.downloadermiddlewares.retry.RetryMiddleware):
            request = failure.request
            self.logger.error(f'RetryMiddleware error on {request.url}')
        else:
            request = failure.request
            self.logger.error(f'Error on {request.url}')

        # Retry the request
        new_request = request.copy()
        yield new_request

    def parse_address(self, address):
        '''
        Cleans up the "City, Zipcode" section of the auction info

        Args:
            address (str): city, zip format

        Returns:
            formatted_address (str): city, state, zip (5 digit) format
        
        '''
        parsed_address = usaddress.tag(address)[0]
        city = parsed_address.get('PlaceName', '')
        
        # Format zip code into standard 5 digit
        zip_code = parsed_address.get('ZipCode', '')[:5]

        formatted_address = f"{city}, OH, {zip_code}"

        return formatted_address
    
    def open_calendar(self):
        urls = ['https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=USER&zmethod=CALENDAR']

        for url in urls:
            yield scrapy.Request(url=url,
                                 meta={
                                     'playwright':True, 
                                     'playwright_include_page' : True
                                 },
                                 callback=self.start_requests)
            
    def start_requests(self):
        urls = ['https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=USER&zmethod=CALENDAR']

        for url in urls:
            yield scrapy.Request(url=url,
                                 meta={
                                     'playwright':True, 
                                     'playwright_include_page' : True
                                 },
                                 callback=self.parse_calendar)
            

            
    def parse_calendar(self, response):
        '''
        Extracts all dates on a given calendar month that has sheriff sales and sends a Request to parse each date of their auction item sales

        Args:
            request for calendar site
        Returns:
            (Yields) requests for each date identified to host auction sales
        
        '''
        dates = response.css('div.CALBOX.CALW5.CALSELF ::attr(dayid)')

        urls = []
        template = 'https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE='

        for date in dates:
            url = template + date.get()

            yield scrapy.Request(url=url,
                                 meta={
                                     'playwright':True, 
                                     'playwright_include_page' : True, 
                                     'playwright_page_methods' : [
                                         PageMethod('wait_for_selector', 'div.AUCTION_ITEM.PREVIEW', timeout=5000), 
                                         PageMethod('wait_for_selector', '[id*=max]', timeout=10000)
                                        ],
                                        'url': url
                                    }, 
                                callback=self.parse,
                                errback=self.errback,
                                dont_filter=True)



    # For single page testing use!!!!

    # def start_requests(self):
    #     urls = [
    #         "https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=08/12/2024",
    #         "https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/17/2024"
    #     ]

    #     for url in urls:
    #         yield scrapy.Request(url=url, 
    #                              errback=self.errback,
    #                              meta={
    #                                  'playwright':True, 
    #                                  'playwright_include_page' : True, 
    #                                  'playwright_page_methods' : [
    #                                      PageMethod('wait_for_selector', 'div.AUCTION_ITEM.PREVIEW', timeout=10000), 
    #                                      PageMethod('wait_for_selector', "#maxCA", timeout=10000),
    #                                     ],
    #                                     'url': url
    #                                 }, 
    #                             callback=self.parse)

    def geocode_address(self, address, item):
        '''
        Opens Nominatim on the OpenStreetMap software for a given address

        Args:
            address: street, state, zip
            item: auction sale item

        Returns:
            (Yields) Request: opens up Nominatum url linked to given address
        
        '''
        url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&addressdetails=1"
        return scrapy.Request(url=url,
                              callback=self.parse_geocode,
                              meta={'item': item, 'address': address})

    def parse_geocode(self, response):
        '''
        Extracts latitude and longitude from Nominatum url of an address

        Args:
            request: the scrapy Request that opens up Nominatum url

        Returns:
            (Yields) auction sale item with geocode field filled in
        
        
        '''
        item = response.meta['item']
        address = response.meta['address']
        if response.status == 200:
            result = response.json()
            if result:
                location = result[0]
                item['geocode'] = {'lat': float(location['lat']), 'lon': float(location['lon'])}
            else:
                item['geocode'] = {'lat': None, 'lon': None}
        else:
            item['geocode'] = {'lat': None, 'lon': None}

        yield item

    
    # TODO: Get start dates working. It loads in a little slower than the rest
    async def assign_auctions_items(self, auction_div, page, max_pages, i, type):

        page.set_default_timeout(10000)

        # Store first auction sale case number to detect changes when switching pages
        if auction_div:
            first_case_number = auction_div[0].css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(2) > td::text').get()

            for ele in auction_div:
                item = SheriffScraperItem()

                item['county'] = 'cuyahoga'
                item['start_date'] = ele.css('div.ASTAT_MSGB.Astat_DATA::text').get()
                item['case_status'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(1) > td::text').get()
                item['case_number'] = (ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(2) > td::text').get()).strip()
                item['parcel_id'] = (ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(3) > td::text').get()).strip()

                item['property_address'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(4) > td::text').get() + ' ' + self.parse_address(ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(5) > td::text').get())

                item['appraised_value'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(6) > td::text').get()
                item['opening_bid'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(7) > td::text').get()
                item['deposit_requirement'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(8) > td::text').get()

                geocode_request = self.geocode_address(item['property_address'], item)
                yield geocode_request # yields whole item after geocoding

            if i < max_pages:

                await page.fill(f'input#curP{type}A', str(i + 1))
                await page.press(f'input#curP{type}A', 'Enter')
                    
                # Wait for the value of the input to change to the next page number

                await page.wait_for_function(
                    f'document.querySelector("div.AUCTION_DETAILS > table > tbody > tr:nth-child(2) > td").textContent != "{first_case_number}"'
                )

                # Wait for dates to show up
                await page.wait_for_timeout(1000)

                
    

    # TODO: Implement running auctions as well --> refer to other parsing loops
    async def parse(self, response):
        '''
        Extracts all information from each auction sale on a given Request

        Args:
            Request: URL of specific date that has auction sales

        Returns:
            (Yields) item: object with auction sale information
        
        '''

        page = response.meta['playwright_page']

        url = response.meta['url']  # Retrieve the URL from meta data

        self.logger.info(f"Parsing page: {url}")  # Log the URL

        #await page.query_selector('div.ASTAT_MSGB.Astat_DATA')

        is_visible_waiting = await page.evaluate("document.querySelector('div.Head_W') && getComputedStyle(document.querySelector('div.Head_W')).display !== 'none';")
        
        if is_visible_waiting:
            max_pages_waiting = int(response.css('#maxWA::text').get())
            
            for i in range(1, max_pages_waiting+1):

                #await page.query_selector('div.ASTAT_MSGB.Astat_DATA')

                content = await page.content()

                response = scrapy.http.HtmlResponse(url=response.url, body=content, encoding='utf-8')

                waiting_auctions = response.css('div#Area_W > div.AUCTION_ITEM.PREVIEW')


                async for item in self.assign_auctions_items(waiting_auctions, page, max_pages_waiting, i, 'W'):
                    yield item


        is_visible_closed = await page.evaluate("document.querySelector('div.Head_C') && getComputedStyle(document.querySelector('div.Head_C')).display !== 'none';")
        
        if is_visible_closed:
            max_pages_closed = int(response.css('#maxCA::text').get())

            for i in range(1, max_pages_closed+1):

                #await page.query_selector('div.ASTAT_MSGB.Astat_DATA')

                content = await page.content()
                response = scrapy.http.HtmlResponse(url=response.url, body=content, encoding='utf-8')

                closed_auctions = response.css('div#Area_C > div.AUCTION_ITEM.PREVIEW')

                async for item in self.assign_auctions_items(closed_auctions, page, max_pages_closed, i, 'C'):
                    yield item
            

        await page.close()