import json
from operator import itemgetter
from scrapy import Item
from .Scraper import Actor, Movie
import re

"""
Source:
https://www.python-course.eu/graphs_python.php
https://www.bogotobogo.com/python/python_graph_data_structures.php
"""

class Vertex:
    def __init__(self, name, age, gross, date, page, isMovie):
        self.name = name
        self.age  = age
        self.gross = gross
        self.date = date
        self.page = page
        self.adjacent = {}
        self.isMoive = isMovie

    """
    Helper function that forms that string for vertex, there are 2 kinds of
    vertex, "actor" vertex and "movie" vertex
    """
    def __str__(self):
        if self.isMoive:
            return "Movie Name: " + str(self.name) + ", Movie Gross: " \
                + str(self.gross) + ", Movie Date: " + str(self.date) + ", Movie Page: " + str(self.page)
        else:
            return "Actor Name: " + str(self.name) + ", Actor age: " \
                + str(self.age) + ", Actor Page: " + str(self.page)

    """
    * Important helper function that adds a new neighbor to a given vertex
    """
    def add_neighbor(self, neighbor, weight):
        self.adjacent[neighbor] = weight

    """
    * Important helper function that return a given vertex's neighbors
    """
    def get_connections(self):
        return self.adjacent.keys()  

    """
    Get the weight of an edge
    """
    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

class myGraph:
    def __init__(self):
        self.vert_dict = {}
        self.movie_vertices = 0
        self.actor_vertices = 0

    """
    Helper funtion to go thru vert_dict
    """
    def __iter__(self):
        return iter(self.vert_dict.values())

    """
    Return all vertices that are "movie" vertices
    """
    def get_all_movie_name(self):
        ret = []
        for i in self.vert_dict.keys():
            if self.vert_dict[i].isMoive:
                ret.append(i)
        return ret

    """
    Return all vertices that are "actor" vertices
    """
    def get_all_actor_name(self):
        ret = []
        for i in self.vert_dict.keys():
            if not self.vert_dict[i].isMoive:
                ret.append(i)
        return ret

    """
    * Important helper function to construct the graph, add vertices to graph
    """
    def add_vertex_to_graph(self, name, age, gross, date, page, isMovie):
        if gross == None:
            self.actor_vertices += 1
        else:
            self.movie_vertices += 1

        new_vertex = Vertex(name, age, gross, date, page, isMovie)
        self.vert_dict[name] = new_vertex
        return new_vertex

    """
    Return the name of the vertex
    """
    def get_vertex_info(self, name):
        if name in self.vert_dict:
            return self.vert_dict[name]
        else:
            return None

    """
    * Important helper function to construct the graph, add egde given a
    movie name and a actor name
    """
    def add_edge(self, actor_name, movie_name, egde_weight):
        if self.vert_dict[actor_name] != None:
                self.vert_dict[actor_name].add_neighbor(movie_name, egde_weight)
        if self.vert_dict[movie_name] != None:
                self.vert_dict[movie_name].add_neighbor(actor_name, egde_weight)
    """
    Helper function that returns that vertex name
    """
    def get_vertices(self):
        return self.vert_dict.keys()

    """
    Given a year, find all the movies release that year
    """
    def get_all_movie_given_year(self, given):
        ret = []
        for i in self.vert_dict.keys():
            if i == None:
                continue
            if self.vert_dict[i].isMoive and self.vert_dict[i].date != None and self.vert_dict[i].date[0:4] == given:
                ret.append(i)
        return ret

    """
    Given a year, first find all the movies release that year, then find all 
    unique casts in those movies
    """
    def get_all_actor_given_year(self, given):
        ret = set()
        for m in self.vert_dict.keys():
            if self.vert_dict[m].isMoive and self.vert_dict[m].date != None and self.vert_dict[m].date[0:4] == given:
                for a in self.get_actors_given_movie(m):
                    ret.add(a)
        return list(ret)

    """
    Given a movie name, return the box office gross
    """    
    def get_movie_gross(self, movie_name):
        if movie_name not in self.vert_dict:
            return "Given movie does not exists in graph!"
        if not self.vert_dict[movie_name].isMoive:
            return "Input is a actor name, please enter a valid movie name!"
        return movie_name + "'s Gross: $" + str(self.vert_dict[movie_name].gross)

    """
    Query the graph to find oldest top K actors
    """
    def get_top_oldest(self, topK):
        ret = []
        for i in self.vert_dict.keys():
            if not self.vert_dict[i].isMoive and self.vert_dict[i].age != None:
                m = re.search(r"\d", self.vert_dict[i].age)
                age = int(self.vert_dict[i].age[m.start(): m.end()+1])
                ret.append((self.vert_dict[i].name, age))
        return sorted(ret, key=lambda x: x[1], reverse=True)[0:topK]

    """
    Query the graph to find the top X actors with the most total grossing value
    """
    def get_topK(self, topK):
        ret = []
        for i in self.vert_dict.keys():
            if not self.vert_dict[i].isMoive:
                total_gross = 0
                for m in self.get_movies_given_actor(self.vert_dict[i].name):
                    if self.vert_dict[m].gross != None:
                        total_gross += self.vert_dict[m].gross
                ret.append((self.vert_dict[i].name, total_gross))
        res = sorted(ret, key=lambda x: x[1], reverse=True)[0:topK]
        return [(x[0], "$"+str(x[1])) for x in res]

    """
    Helper function that retrive a particular movie information
    """
    def get_movie_info(self, given_name):
        if given_name not in self.vert_dict:
            return "No such movie found!"
        ret = self.vert_dict[given_name]
        return ("Movie Name: " + ret.name + "\nGross: $" + \
                str(ret.gross) + "\nRelease Date: " + str(ret.date) + \
                "\nWiki Page: " + ret.page)

    """
    Helper function that retrive a particular actor information
    """
    def get_actor_info(self, given_name):
        if given_name not in self.vert_dict:
            return "No such actor found!"
        ret = self.vert_dict[given_name]
        return ("Actor Name: " + ret.name + "\nAge: " + \
                str(ret.age) + "\nWiki Page: " + ret.page)
    
    """
    Given an actor, list which movies the given actor has worked in
    """
    def get_movies_given_actor(self, actor_name):
        if actor_name not in self.vert_dict:
            return "Given actor does not exists in graph!"
        return list(self.vert_dict[actor_name].get_connections())

    """
    Given a movie, list which actors worked in a movie
    """
    def get_actors_given_movie(self, movie_name):
        if movie_name not in self.vert_dict:
            return "Given movie does not exists in graph!"
        return list(self.vert_dict[movie_name].get_connections())

    """
    Function that computes which actors have the most connection with other actors
    """
    def get_hub_actors(self):
        ret = {}
        for i in self.vert_dict.keys():
            if not self.vert_dict[i].isMoive:
                ret[i] = 0
                for cur_movie in self.get_movies_given_actor(i):
                    ret[i] += (len(self.get_actors_given_movie(cur_movie)) - 1)

        highest = max(ret.values())
        hub = [str(k) + " with largest connection of " + str(v) + "\n" for k, v in ret.items() if v == highest]
        return ''.join(hub)

    """
    Function that return all actors' age and their total gross in all movie
    """
    def get_correlation(self):
        age = []
        earning = []
        for i in self.vert_dict.keys():
            if not self.vert_dict[i].isMoive and self.vert_dict[i].age != None:
                if isinstance(self.vert_dict[i].age, int):
                    if self.vert_dict[i].age == 0 or self.vert_dict[i].gross == 0:
                        continue
                    age.append(self.vert_dict[i].age)
                    earning.append(self.vert_dict[i].gross)
                else:
                    m = re.search(r"\d", self.vert_dict[i].age)
                    actor_earning = sum(self.vert_dict[i].adjacent.values())
                    actor_age = int(self.vert_dict[i].age[m.start(): m.end()+1])
                    if actor_age == 0 or actor_earning == 0:
                        continue
                    age.append(actor_age)
                    earning.append(actor_earning)
        res = {}
        for i in range(len(age)):
            cur_age = int(5 * round(float(age[i])/5))
            if cur_age not in res:
                res[cur_age] = [1, earning[i]]
            else:
                res[cur_age][0] += 1
                res[cur_age][1] += earning[i]
        for key, value in res.items():
            res[key] = value[1]/value[0]

        highest = max(res.values())
        winner = ["Age around " + str(k) + " has the highest average earning of $" + str(int(v)) for k, v in res.items() if v == highest]
        return age, earning, winner[0]

    """
    Helper function to update parameters
    """
    def update_name(self, name, target):    
        ret = self.vert_dict[name]
        if ret != None:
            self.vert_dict[str(target)] =  self.vert_dict[name]
            self.vert_dict[str(target)].name = str(target)
    def update_age(self, name, target):    
        ret = self.vert_dict[name]
        if ret != None and not ret.isMoive:
            self.vert_dict[name].age = int(target)
    def update_gross(self, name, target):    
        ret = self.vert_dict[name]
        if ret != None:
            self.vert_dict[name].gross = int(target)
    def update_date(self, name, target):    
        ret = self.vert_dict[name]
        if ret != None and ret.isMoive:
            self.vert_dict[name].date = int(target)
    def update_page(self, name, target):    
        ret = self.vert_dict[name]
        if ret != None:
            self.vert_dict[name].page = str(target)

    """
    Helper function to delete actor object
    """
    def delete_vertex(self, name):
        cur_vertex = self.vert_dict[name]
        if cur_vertex == None:
            return False
        for key, neighbor in cur_vertex.adjacent.items():
            del self.vert_dict[key].adjacent[name]
        del self.vert_dict[name]
        return True