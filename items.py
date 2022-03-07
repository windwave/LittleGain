# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    follow_num = scrapy.Field()
    fans_num = scrapy.Field()

class PortfolioItem(scrapy.Item):
    portfolio_id = scrapy.Field()
    portfolio_totalAction = scrapy.Field()

    