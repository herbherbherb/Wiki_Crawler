import scrapy
from scrapy import Item

class Actor(scrapy.Item):
	actor_name = scrapy.Field()
	actor_age = scrapy.Field()
	page = scrapy.Field()

class Movie(scrapy.Item):
	name = scrapy.Field()
	gross = scrapy.Field()
	date = scrapy.Field()
	actors = scrapy.Field()
	page = scrapy.Field()