import re
import scrapy
from scrapy import Spider
from bs4 import BeautifulSoup
from dateparser import parse as parse_date
from .item import Actor, Movie
import config
"""
Source: 
https://github.com/alecxe/scrapy-fake-useragent
https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/
https://github.com/horizon-blue/wiki-crawler
"""

wiki_root = "https://en.wikipedia.org"
wiki_start = config.wiki_start
# wiki_start = "https://en.wikipedia.org/wiki/Johnny_Depp"
# wiki_start = "https://en.wikipedia.org/wiki/Jennifer_Lawrence"
divider = "============================================================================"

class MySpider(scrapy.Spider):
	allowed_domains = ["en.wikipedia.org"]
	name = "uniqueSpider"
	custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
        },
        "EXTENSIONS": {
            "scrapy.extensions.closespider.CloseSpider": 1,
        },
         "ITEM_PIPELINES": {
            "model.Scraper.pipeline.JsonWriterPipeline": 300,
        },
        "CLOSESPIDER_ITEMCOUNT": config.CLOSESPIDER_ITEMCOUNT,
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 0.1,
    }

	"""
	* Parse function that scrappy will call
	"""
	def start_requests(self):
		yield scrapy.Request(wiki_start, meta={'_movie_': False, '_movie_list_': False})

	"""
	* Parse function that scrappy will call
	"""
	def parse(self, response):
		if response.meta["_movie_"] == True:
			yield from self.movie_parser(response)
		elif response.meta["_movie_list_"] == True:
			yield from self.movieList_parser(response)
		else:
			yield from self.actor_parser(response)

	"""
	* Function to parse given movie information, include movie name, movie grossing, movie date, movie casts included, and wiki page link
	"""
	def movie_parser(self, response):
		ret = {}
		try:
			bs, movie_name = self.parser_helper(response)
			movie_actor = self.get_movie_actor(bs)
			movie_gross = self.get_movie_gross(bs)
			new_movie = Movie(name=movie_name, gross=movie_gross, \
				date=self.get_movie_date(bs), actors=movie_actor, page=response.request.url)
			yield new_movie
			for cast in movie_actor:
				if movie_gross != None:
					yield scrapy.Request(wiki_root + cast, meta={'_movie_': False, '_movie_list_': False})
		except AttributeError:
			yield ret

	"""
	* Helper function that extract movie’s release date, information is crawled from the side panel
	"""
	def get_movie_date(self, bs):
		movie_date = None
		try:
			movie_date = bs.find("table", attrs={"class": "infobox"}).find("span", attrs={"class": "bday dtstart published updated"}).text
		except AttributeError:
			pass
		return movie_date

	"""
	* Given a movie, find all the casts that play this movie. Crawl the info from side panel.
	"""
	def get_movie_actor(self, bs):
		movie_actor = []
		try:
			casts = bs.find("table", attrs={"class": "infobox"}).find(text="Starring").find_parent("tr").find_all("a")
			for cast in casts:
				if cast.has_attr('href') and not cast['href'].startswith("#"):
					movie_actor.append(cast['href'])
		except AttributeError:
			pass
		return movie_actor

	"""
	* Helper function that converts string currency value into float
	"""
	def get_movie_gross(self, bs):
		ret = None
		try:
			movie_gross = bs.find("table", attrs={"class": "infobox"}).find(text="Box office").find_parent() \
				.find_next_sibling().next_element.strip()
			ret = float(movie_gross.replace(r"[(\[].*[)\][^\d.]", "").replace(" ", "").strip('$trbmilon'))
			if "million" in movie_gross or "Million" in movie_gross:
				ret *= 1e6
			if "billion" in movie_gross or "Billion" in movie_gross:
				ret *= 1e9
			if "trillion" in movie_gross or "Trillion" in movie_gross:
				ret *= 1e12
			return ret
		except (AttributeError, TypeError, ValueError):
			return ret

	"""
	* Function to parse actor information, include name, age, and page
	"""
	def actor_parser(self, response):
		ret = {}
		try:
			bs, actor_name = self.parser_helper(response)
			new_actor = Actor(actor_name=actor_name, actor_age=self.age_parser(bs), page=response.request.url)
			film_starting_point = bs.find("span", id="Filmography")
			if film_starting_point == None:
				film_starting_point = bs.find("span", id="Selected_filmography")
				if film_starting_point == None:
					yield new_actor

			film_starting_point =  film_starting_point.find_parent("h2").find_next_sibling()

			if "Main" in film_starting_point.get_text():
				article_link = film_starting_point.find("a")
				if article_link.has_attr('href') and not article_link["href"].startswith("#"):
					href = article_link["href"]
					yield scrapy.Request(wiki_root + href, meta={'_movie_': False, '_movie_list_': True})
			else:
				for next_movie in self.directly_crawl(bs):
					yield scrapy.Request(wiki_root + next_movie, meta={'_movie_': True, '_movie_list_': False})
			yield new_actor
		except AttributeError:
			yield ret

	"""
	* If there is for Main article link to click in, then it means the corresponding movie table are under the actor’s page
	"""
	def directly_crawl(self, bs):
		films_hrefs = []
		table_starting_point =  bs.find("span", id="Filmography").find_parent("h2") \
				.find_next_sibling().find_next_sibling()
		th_attr = table_starting_point.find_all("th")
		hrefs = [th.find("a") for th in th_attr]
		for href in hrefs:
			if href != None and href.has_attr('href') and not href["href"].startswith("#"):
				films_hrefs.append(href['href'])
		return films_hrefs

	"""
	* This is to crawl the movie lists that on a given page, those movies all contain at least 1 common actors.
	* Find the first table that contain hyper link and only crawl titles hyper link. 
	"""
	def movieList_parser(self, response):
		ret = {}
		bs = BeautifulSoup(response.text, 'lxml')
		target_table = None
		for t in bs.find_all("table"):
			if t.find('a') != None:
				target_table = t
				break
		if target_table == None:
			yield {}
		else:	
			th_attr = target_table.find_all("th")
			hrefs = [th.find("a") for th in th_attr]
			for href in hrefs:
				if href != None and href.has_attr('href') and not href["href"].startswith("#"):
					yield scrapy.Request(wiki_root + href['href'], meta={'_movie_': True, '_movie_list_': False})

	"""
	* Parse the age from actor page, there are 2 types, actors can be dead or alive
	"""
	def age_parser(self, bs):
		age = 0 
		try: 
			actor_age = bs.find("table", attrs={"class": "infobox"}).find("span", attrs={"class": "noprint ForceAgeToShow"})
			if actor_age != None:
				age = actor_age.get_text().strip()
			else:
				bs.prettify(formatter=lambda s: s.replace(u'\xa0', ' '))
				age = bs.find("table", attrs={"class": "infobox"}) \
						.find("th", string="Died").find_next_sibling() \
						.get_text().strip()
				age = "Died: " + age[age.find('(') : (age.rfind(')') + 1)]
		except AttributeError:
			age = None
		return age

	"""
	* Generic parser helper that initialize a beautiful soup instance and get the heading for the actors/movies
	"""
	def parser_helper(self, response):
		bs = BeautifulSoup(response.text, 'lxml')
		actor_name = bs.find(id="firstHeading").text.replace(r"\(.*\)", "").strip()
		return bs, actor_name
