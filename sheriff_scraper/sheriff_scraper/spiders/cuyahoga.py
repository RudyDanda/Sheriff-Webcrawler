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

    # FIND ALL ONES WITH "dayid" and then append those to urls

    # def errback(self, failure):
    #     self.logger.error(f"Request failed: {failure}")
    #     request = failure.request
    #     retries = request.meta.get('retry_times', 0) + 1
    #     max_retries = self.custom_settings.get('RETRY_TIMES', 5)

    #     if retries <= max_retries:
    #         self.logger.info(f"Retrying {request.url} (Retry {retries}/{max_retries})")
    #         retry_req = request.copy()
    #         retry_req.meta['retry_times'] = retries
    #         yield retry_req
    #     else:
    #         self.logger.error(f"Gave up on {request.url} after {max_retries} retries")

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
            
    # def start_requests(self):
    #     urls = ['https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=USER&zmethod=CALENDAR']

    #     for url in urls:
    #         yield scrapy.Request(url=url,
    #                              meta={
    #                                  'playwright':True, 
    #                                  'playwright_include_page' : True
    #                              },
    #                              callback=self.parse_calendar)
            

            
    def parse_calendar(self, response):
        dates = response.css('div.CALBOX.CALW5.CALSELF ::attr(dayid)')

        urls = []
        template = 'https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE='

        for date in dates:
            urls.append(template + date.get())

        for url in urls:
            yield scrapy.Request(url=url, 
                                 #errback=self.errback,
                                 meta={
                                     'playwright':True, 
                                     'playwright_include_page' : True, 
                                     'playwright_page_methods' : [
                                         PageMethod('wait_for_selector', 'div.AUCTION_ITEM.PREVIEW', timeout=5000), 
                                         PageMethod('wait_for_selector', "#maxCA", timeout=5000),
                                        ]
                                    }, 
                                callback=self.parse,
                                errback=self.errback)



    # For single page testing use!!!!

    def start_requests(self):
        urls = [
            #"https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/22/2024",
            "https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/29/2024"
        ]

        for url in urls:
            yield scrapy.Request(url=url, 
                                 #errback=self.errback,
                                 meta={
                                     'playwright':True, 
                                     'playwright_include_page' : True, 
                                     'playwright_page_methods' : [
                                         PageMethod('wait_for_selector', 'div.AUCTION_ITEM.PREVIEW', timeout=10000), 
                                         PageMethod('wait_for_selector', "[id^='max']", timeout=10000),
                                        ]
                                    }, 
                                callback=self.parse)
            

    
    # TODO: Get start dates working. It loads in a little slower than the rest
    async def assign_auctions_items(self, auction_div, page, max_pages, i, type):

        page.set_default_timeout(10000)

        # Store first auction sale case number to detect changes when switching pages
        if auction_div:
            first_case_number = auction_div[0].css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(2) > td::text').get()

            for ele in auction_div:
                item = SheriffScraperItem()

                item['start_date'] = ele.css('div.ASTAT_MSGB.Astat_DATA::text').get()
                item['case_status'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(1) > td::text').get()
                item['case_number'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(2) > td::text').get()
                item['parcel_id'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(3) > td::text').get()

                item['property_address'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(4) > td::text').get() + ' ' + self.parse_address(ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(5) > td::text').get())

                item['appraised_value'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(6) > td::text').get()
                item['opening_bid'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(7) > td::text').get()
                item['deposit_requirement'] = ele.css('div.AUCTION_DETAILS > table > tbody > tr:nth-child(8) > td::text').get()

                yield item

            if i < max_pages:
                #await page.wait_for_timeout(3000)
                await page.fill(f'input#curP{type}A', str(i + 1))
                await page.press(f'input#curP{type}A', 'Enter')
                    
                # Wait for the value of the input to change to the next page number

                #try:
                await page.wait_for_function(
                    f'document.querySelector("div.AUCTION_DETAILS > table > tbody > tr:nth-child(2) > td").textContent != "{first_case_number}"'
                )

                                            # if something breaking..
                                            # remove "dive#Area{type} >"


                    

                # TODO: enclose the wait_for_function part in a try except case (except timeout, then that red notice pops up from number entered over max_pages)
                # TODO: instead of hard code timeout for date, wait for auction start date details to show up

                # Wait for dates to show up
                await page.wait_for_timeout(1000)

                
    

    # TODO: Implement running auctions as well --> refer to other parsing loops
    async def parse(self, response):

        
        page = response.meta['playwright_page']
        #await page.query_selector('div.ASTAT_MSGB.Astat_DATA')

        max_pages_waiting = int(response.css('#maxWA::text').get())
        for i in range(1, max_pages_waiting+1):

            #await page.query_selector('div.ASTAT_MSGB.Astat_DATA')

            content = await page.content()

            response = scrapy.http.HtmlResponse(url=response.url, body=content, encoding='utf-8')

            waiting_auctions = response.css('div#Area_W > div.AUCTION_ITEM.PREVIEW')


            async for item in self.assign_auctions_items(waiting_auctions, page, max_pages_waiting, i, 'W'):
                yield item


        max_pages_closed = int(response.css('#maxCA::text').get())

        for i in range(1, max_pages_closed+1):

            #await page.query_selector('div.ASTAT_MSGB.Astat_DATA')

            content = await page.content()
            response = scrapy.http.HtmlResponse(url=response.url, body=content, encoding='utf-8')

            closed_auctions = response.css('div#Area_C > div.AUCTION_ITEM.PREVIEW')

            async for item in self.assign_auctions_items(closed_auctions, page, max_pages_closed, i, 'C'):
                yield item
            

        await page.close()



        # if response.meta['cur_page'] != response.meta['max_pages']:
        #     yield scrapy.Request(response.url, callback=self.parse, meta={
        #         "playwright" : True,
        #         "playwright_include_page" : True,
        #         'playwright_page_methods' : [
        #             PageMethod('fill', 'input#curPWA', str(response.meta['cur_page'] + 1) ),
        #             PageMethod('press', 'input#curPWA', 'Enter'),
        #             #PageMethod('wait_for_timeout', 3000),
        #             PageMethod('wait_for_selector', 'div.AUCTION_ITEM.PREVIEW', timeout=10000), 
        #             PageMethod('wait_for_selector', 'input#curPWA', timeout=10000),
        #         ],
        #         'cur_page' : response.meta['cur_page'] + 1,
        #         'dont_filter' : True
        #     })





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
        


