from pathlib import Path
from typing import Iterable


import scrapy
from scrapy_playwright.page import PageMethod


class SheriffSpider(scrapy.Spider):
    name = "cuyahoga"
    allowed_domains = ['cuyahoga.sheriffsaleauction.ohio.gov']

    # async def errback(self, failure):
    #     page = failure.request.meta["playwright_page"]
	# 	await page.close()

    def start_requests(self):
        urls = [
            "https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/22/2024",
            "https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/29/2024"
        ]

        for url in urls:
            yield scrapy.Request(url=url, meta={'playwright':True, 'playwright_include_page' : True, 'playwright_page_methods' : [PageMethod('wait_for_selector', 'div.AUCTION_ITEM.PREVIEW')]}, callback=self.parse)

    # def start_requests(self):
    #     urls = [
    #         "https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/22/2024",
    #         "https://cuyahoga.sheriffsaleauction.ohio.gov/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=07/29/2024"
    #     ]

    #     for url in urls:
    #         yield scrapy.Request(
    #             url=url, 
    #             meta={'playwright':True}, 
    #             callback=self.parse)

    def parse(self, response):

        #sales = await response.xpath('//*[contains(@class, "AUCTION_ITEM PREVIEW")]')
        sales = response.css('div.AUCTION_ITEM.PREVIEW')
        #sales = response.css('div.Loading')
        print("sales: ", sales)
        # for ele in sales:
        #     sale_item = SheriffSaleItem()
        #     sale_item['case_number'] = ele.css('div')
        #     label = row.css('th::text').get()
        #     value = row.css('td::text').get()
        #     yield value

    # def parse(self, response):
    #     rows = response.css('#AITEM_35533 .AUCTION_DETAILS .ad_tab tbody tr')
    #     data = {}
    #     for row in rows:
    #         label = row.css('th::text').get()
    #         value = row.css('td::text').get()
    #         if label and value:
    #             # Clean up the label to use it as a dictionary key
    #             label = label.strip().replace(':', '')
    #             data[label] = value.strip()
    #     yield data

