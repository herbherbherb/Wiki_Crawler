import scrapy
from scrapy import log
from scrapy.crawler import CrawlerProcess
from model.Scraper import MySpider
from model.graphy import myGraph
from model.Scraper import Actor, Movie
import json_lines
import logging
import sys
import termios
import contextlib
import time
import re
import numpy as np
import matplotlib.pyplot as plt
import json
import igraph
from igraph import *
"""
Source: 
https://stackoverflow.com/questions/13437402/how-to-run-scrapy-from-within-a-python-script
https://stackoverflow.com/questions/11918999/key-listeners-in-python
https://github.com/vBlackOut/vHackOS-Python/blob/master/utils.py
"""
divider = "============================================================================"
prompt = "\n Press a number to query graph: \n \
1. Find how much a movie has grossed \n \
2. List which movies an actor has worked in \n \
3. List which actors worked in a movie \n \
4. List the top X actors with the most total grossing value \n \
5. List the oldest X actors \n \
6. List all the movies for a given year \n \
7. List all the actors for a given year \n \
8. Show list of movies  \n \
9. Show list of actors \n \
10. Total number of movies \n \
11. Total Number of actors \n \
12. Show given movie info \n \
13. Show given actor info \n \
14. Identify 'hub' actors \n \
15. Calculate age and grossing value correlation and generate plot -> correlation.png \n \
=> "
total_movie = 0
total_actor = 0
my_graph = None

"""
* Important helper function that responds to user's keyboard input
 and conduct graph query, base on different keyboard input, it answer
 the query differently
"""
def answer(mystr, g):
	inputList = mystr.strip().split()
	if(len(inputList) > 1 and inputList[0] == '1'):
		movie_name = " ".join(inputList[1:])
		ret = g.get_movie_gross(movie_name)
		if ret == None:
			myprint("Can not find gross for " + movie_name + "!")
			return
		myprint(ret)
	if(len(inputList) > 1 and inputList[0] == '2'):
		actor_name = " ".join(inputList[1:])
		ret = g.get_movies_given_actor(actor_name)
		if len(ret) == 0:
			myprint("This actor has no corresponding movie!")
			return
		myprint(ret)
	if(len(inputList) > 1 and inputList[0] == '3'):
		movie_name = " ".join(inputList[1:])
		ret = g.get_actors_given_movie(movie_name)
		if len(ret) == 0:
			myprint("This movie has no corresponding actor!")
			return
		myprint(ret)
	if(len(inputList) == 2 and inputList[0] == '4'):
		try:
			topK = int(inputList[1])
			k = 1
			ret = g.get_topK(topK)
			if ret == None or len(ret) == 0:
				myprint("Second argument must be a valid integer!")
				return
			print(divider)
			for i in ret:
				if(k % 4 == 0):
					print()
				print(i, end=" ")
				k += 1
			print()
			print(divider)
		except (TypeError, ValueError):
			myprint("Second argument must be a valid integer!")

	if(len(inputList) == 2 and inputList[0] == '5'):
		try:
			oldest = int(inputList[1])
			k = 1
			ret = g.get_top_oldest(oldest)
			if ret == None or len(ret) == 0:
				myprint("Second argument must be a valid integer!")
				return
			print(divider)
			for i in ret:
				if(k % 4 == 0):
					print()
				print(i, end=" ")
				k += 1
			print()
			print(divider)
		except (TypeError, ValueError):
			myprint("Second argument must be a valid integer!")

	if(len(inputList) == 2 and inputList[0] == '6'):
		ret = g.get_all_movie_given_year(inputList[1])
		if len(ret) == 0:
			myprint("No movies in year " + inputList[1])
			return
		myprint(ret)
	if(len(inputList) == 2 and inputList[0] == '7'):
		ret = g.get_all_actor_given_year(inputList[1])
		if len(ret) == 0:
			myprint("No actors in year " + inputList[1])
			return
		myprint(ret)
	if(len(inputList) == 1 and inputList[0] == '8'):
		myprint(g.get_all_movie_name())
	if(len(inputList) == 1 and inputList[0] == '9'):
		myprint(g.get_all_actor_name())
	if(len(inputList) == 1 and inputList[0] == '10'):
		myprint("Total Number of movies: " + str(total_movie))
	if(len(inputList) == 1 and inputList[0] == '11'):
		myprint("Total Number of actors: " + str(total_actor))
	if(len(inputList) > 1 and inputList[0] == '12'):
		movie_name = " ".join(inputList[1:])
		myprint(g.get_movie_info(movie_name))
	if(len(inputList) > 1 and inputList[0] == '13'):
		actor_name = " ".join(inputList[1:])
		myprint(g.get_actor_info(actor_name))
	if(len(inputList) == 1 and inputList[0] == '14'):
		myprint(g.get_hub_actors())
	if(len(inputList) == 1 and inputList[0] == '15'):
		age, earning, summary = g.get_correlation()
		myprint(summary + "\nCorrelation matrix: \n" + str(np.corrcoef(age, earning)))
		plt.plot(age, earning, 'ro')
		plt.axis([0, max(age), min(earning), max(earning)])
		plt.savefig('correlation.png')

def read_input(json_file):
	g = myGraph()
	actor_list = []
	actor_name = set()
	movie_list = []
	json_str = json_file.read()
	actor_data = json.loads(json_str)[0]
	movie_data = json.loads(json_str)[1]
	num_actor = 0
	num_movie = 0
	vertices = []
	edges = []
	item = {}

	# vertices = ["one", "two", "three"]
	# edges = [(0,2),(2,1),(0,1)]
	for key, value in actor_data.items():
		if value['json_class'] == "Actor":
			actor_name.add(key)
			num_actor += 1
			g.add_vertex_to_graph(value['name'], value['age'], value['total_gross'], None, "", False)
			item[value['name']] = len(vertices)
			vertices.append(value['name'])
		else:
			continue
	for key, value in movie_data.items():
		if value['json_class'] == "Movie":
			num_movie += 1
			g.add_vertex_to_graph(value['name'], None, value['box_office'], value['year'], value['wiki_page'], True)
			item[value['name']] = len(vertices)
			vertices.append(value['name'])
			for actor in value['actors']:
				if actor not in actor_name:
					continue
				g.add_edge(actor, value['name'], value['box_office'])
				edges.append((item[actor], item[value['name']]))
		else:
			continue

	global total_actor 
	global total_movie
	total_actor = num_actor
	total_movie = num_movie


	graph = Graph(vertex_attrs={"label": vertices}, edges=edges, directed=False)
	Graph.write_svg(graph, "graph_input.svg")
	return g

"""
Function to construct the graph structure, get ready for graph query
"""
def constructor_graph(f):
	g = myGraph()
	actor_list = []
	actor_name = set()
	movie_list = []
	vertices = []
	edges = []
	items = {}
	total_edge = 0
	for item in json_lines.reader(f):
		# def add_vertex_to_graph(self, name, age, gross, date, page):
		if ('actor_name' in item):
			# print(item['actor_name'], item['actor_age'])
			actor_list.append(item)
			actor_name.add(item['actor_name'])
			g.add_vertex_to_graph(item['actor_name'], item['actor_age'], None, None, item['page'], False)
			actor_detail = "Actor: " + item['actor_name'] + "\nAge: " + str(item['actor_age'])
			items[item['actor_name']] = len(vertices)
			vertices.append(actor_detail)
		else:
			movie_list.append(item)
			g.add_vertex_to_graph(item['name'], None, item['gross'], item['date'], item['page'], True)
			movie_detail = "Movie: " + item['name'] + "\n Total Gross: " + str(item['gross'])
			items[item['name']] = len(vertices)
			vertices.append(movie_detail)

	for m in movie_list:
		gross = m['gross']
		movie_name = m['name']
		i = 1
		for actor in m['actors']:
			cur_name = actor[actor.rfind("/")+1: ].replace("_", " ")
			if cur_name not in actor_name:
				continue
			egde_weight = gross * (1 + i*0.0001)
			i += 1
			g.add_edge(cur_name, movie_name, egde_weight)
			total_edge += 1
			edges.append((items[cur_name], items[movie_name]))

	global total_actor 
	global total_movie
	total_actor = len(actor_list)
	total_movie = len(movie_list)

	print(total_edge)
	graph = Graph(vertex_attrs={"label": vertices}, edges=edges, directed=False)
	Graph.write_svg(graph, fname="graph_cache.svg", labels='label', colors="blue", vertex_size=3, edge_colors=["yellow"]*1000, font_size="4")
	return g

"""
Listen for user's keyboard input and call answer function for grapy query
"""
def listen(g):
	myprint("(Press ^C or ^Z to Exit)")
	while True:
		variable = input(prompt)
		answer(variable, g)

"""
Helper function to print string
"""
def myprint(mystring):
	print(divider)
	print(mystring)
	print(divider)

"""
Main function, control logic
"""
def main():
	if len(sys.argv) == 2 and sys.argv[1] == "cache":
		try:
			f = open('items.jl', 'rb')
			g = constructor_graph(f)
			listen(g)
			exit()
		except FileNotFoundError:
			myprint("No Cached JSON File")
			exit()
	elif len(sys.argv) == 2 and sys.argv[1] == "scrap":
		myprint("Start Scraping...")
		process = CrawlerProcess()
		process.crawl(MySpider)
		process.start()
		myprint("Scraping Finished")
		try:
			f = open('items.jl', 'rb')
			g = constructor_graph(f)
			listen(g)
			exit()
		except FileNotFoundError:
			myprint("Scrapped JSON cannot be opened, please try again...")
			exit()
	elif len(sys.argv) == 2 and sys.argv[1] == "input":
		try:
			json_file = open('data.json')
			g = read_input(json_file)
			listen(g)
			exit()
		except FileNotFoundError:
			myprint("No Input JSON File")
			exit()
	else:
		myprint("Invalid Argument, exit...")
		exit()
	
if __name__ == "__main__":
	main()
