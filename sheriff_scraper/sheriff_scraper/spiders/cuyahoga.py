from pathlib import Path
from typing import Iterable
from sheriff_scraper.items import SheriffScraperItem


import scrapy
from scrapy_playwright.page import PageMethod

import usaddress


class SheriffSpider(scrapy.Spider):
    name = "cuyahoga"
    allowed_domains = ['cuyahoga.sheriffsaleauction.ohio.gov']
    max_retries = 3

    # async def errback(self, failure):
    #     page = failure.request.meta["playwright_page"]
	# 	await page.close()

    def errback(self, failure):
        self.logger.error(f"Request failed: {failure}")
        request = failure.request
        retries = request.meta.get('retry_times', 0) + 1
        max_retries = self.custom_settings.get('RETRY_TIMES', 5)

        if retries <= max_retries:
            self.logger.info(f"Retrying {request.url} (Retry {retries}/{max_retries})")
            retry_req = request.copy()
            retry_req.meta['retry_times'] = retries
            yield retry_req
        else:
            self.logger.error(f"Gave up on {request.url} after {max_retries} retries")

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
    


    def start_requests(self):
        urls = [
            #"https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/22/2024",
            "https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/15/2024"
        ]

        for url in urls:
            yield scrapy.Request(url=url, 
                                 #errback=self.errback,
                                 meta={
                                     'playwright':True, 
                                     'playwright_include_page' : True, 
                                     'playwright_page_methods' : [PageMethod('wait_for_selector', 'div.AUCTION_ITEM.PREVIEW', timeout=10000)], 
                                     'retry_count' : 0}, 
                                callback=self.parse)
            

    def parse(self, response):
        #page.wait_for_selector('div.AUCTION_ITEM.PREVIEW', timeout=5000)
        # If selector found, process page

            
        auction_div = response.css('div.AUCTION_ITEM.PREVIEW')

        # TODO: Implement feature that clicks on next page button on each url
        # Idea: have double for loop --> outer for loop is iterating each page
        
        for ele in auction_div:
            item = SheriffScraperItem()

            item['start_date'] = ele.css('div.ASTAT_MSGB.Astat_DATA::text').get()
            item['case_status'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(1) > td::text').get()
            item['case_number'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(2) > td::text').get()
            item['parcel_id'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(3) > td::text').get()

            item['property_address'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(4) > td::text').get() + ' ' + self.parse_address(ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(5) > td::text').get())
            #print(ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(4) > td::text').get() + ' ' + self.parse_address(ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(5) > td::text').get()))

            item['appraised_value'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(6) > td::text').get()
            item['opening_bid'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(7) > td::text').get()
            item['deposit_requirement'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(8) > td::text').get()

            yield item



    # def parse(self, response):

    #     page = response.meta['playwright_page']
    #     retry_count = response.meta['retry_count']

    #     try:
    #         #page.wait_for_selector('div.AUCTION_ITEM.PREVIEW', timeout=5000)
    #         # If selector found, process page
    #         self.log("Element loaded successfully.")
    #         print("Element loaded successfully.")
            
    #         auction_div = response.css('div.AUCTION_ITEM.PREVIEW')
    #         print('hi')
    #         print(auction_div)

    #         # TODO: Implement feature that clicks on next page button on each url
    #         for ele in auction_div:
    #             item = SheriffScraperItem()

    #             item['start_date'] = ele.css('div.ASTAT_MSGB.Astat_DATA::text').get()
    #             item['case_status'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(1) > td::text').get()
    #             item['case_number'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(2) > td::text').get()
    #             item['parcel_id'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(3) > td::text').get()

    #             item['property_address'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(4) > td::text').get() + ' ' + self.parse_address(ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(5) > td::text').get())
    #             print(ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(4) > td::text').get() + ' ' + self.parse_address(ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(5) > td::text').get()))

    #             item['appraised_value'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(6) > td::text').get()
    #             item['opening_bid'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(7) > td::text').get()
    #             item['deposit_requirements'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(8) > td::text').get()

    #             yield item

    #     except Exception as e:
    #         if retry_count < self.max_retries:
    #             self.log(f"Element did not render in time... reloading page... retry count: {retry_count}")
    #             print(f"Element did not render in time... reloading page... retry count: {retry_count}")
    #             retry_count += 1

    #             # Reload page and try again
    #             yield scrapy.Request(
    #                 url=response.url,
    #                 meta={
    #                     'playwright': True,
    #                     'playwright_include_page' : True,
    #                     'playwright_page_methods': [
    #                         PageMethod('reload'),
    #                         PageMethod('wait_for_selector', 'div.AUCTION_ITEM.PREVIEW', timeout=5000)
    #                     ],
    #                     'retry_count' : retry_count
    #                 },
    #                 callback=self.parse,
    #                 dont_filter=True
    #             )

    #         else:
    #             self.log(f"Element did not load after {self.max_retries} retries.")
    #             print(f"Element did not load after {self.max_retries} retries.")
        


