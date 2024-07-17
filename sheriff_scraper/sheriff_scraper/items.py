# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SheriffScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    start_date = scrapy.Field()
    case_status = scrapy.Field()
    case_number = scrapy.Field()
    parcel_id = scrapy.Field()
    property_address = scrapy.Field()
    appraised_value = scrapy.Field()
    opening_bid = scrapy.Field()
    deposit_requirement = scrapy.Field()
