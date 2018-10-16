from scrapy.exceptions import DropItem
import json
from .item import Actor, Movie
import logging

"""
Source: 
https://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""

class JsonWriterPipeline(object):
	"""
	OPen spider once it is done
	"""
	def open_spider(self, spider):
		self.file = open('items.jl', 'w')
		self.movie_count = 0
		self.actor_count = 0

	"""
	Close spider once it is done
	"""
	def close_spider(self, spider):
		self.file.close()

	"""
	Pipeline for scrappy to process each item
	"""
	def process_item(self, item, spider):
		try:
			if isinstance(item, Movie):
				if not item.get("actors"):
					logging.warning("Currecntly processing movie: {}, missing casts list!".format(item["name"])) 
					raise ValueError("Missing casts list!")
				if item.get("gross") is None:
						logging.warning("Currecntly processing movie: {}, missing movie gross!".format(item["name"])) 
						raise ValueError("Missing movie gross!")
			if isinstance(item, Actor):
			    self.actor_count += 1
			else:
			    self.movie_count += 1
			logging.info(
			    "Currecntly Processing {} @ {}. "
			    "Current Progress - movies: {}, actors: {}".format(
			        item.__class__.__name__, item["page"], self.movie_count, self.actor_count))
			line = json.dumps(dict(item)) + "\n"
			self.file.write(line)
			return item
		except (KeyError, ValueError):
			logging.error("Current item {} has incomplete information, cannot be processed!".format(item["name"])) 
			raise DropItem("Incomplete info in %s" % item)