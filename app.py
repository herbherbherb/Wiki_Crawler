from flask import Flask, jsonify
from flask import abort
from flask import request
from model.Scraper import MySpider
from model.graphy import myGraph
from model.Scraper import Actor, Movie
import json_lines
import termios
import contextlib
import time
import re
import numpy as np
import matplotlib.pyplot as plt
import json
import config

global g
app = Flask(__name__)

def read_input(json_file):
    g = myGraph()
    global actor_name 
    global movie_name 
    actor_name = set()
    movie_name = set()
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
            movie_name.add(key)
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

    return g


"""
/actors?attr={attr_value} Example: /actors?name=”Bob”

Filters out all actors that don’t have “Bob” in their name 
(Should allow for similar filtering for any other attribute)
You should also be able to filter using boolean operators AND and OR, 
i.e. name=”Bob”|name=”Matt”, name=”Bob”&age=35
"""
@app.route('/actors', methods=['GET'])
def filter_actor():
    # request.args.to_dict()
    # request.args.getlist('attr')
    target = request.args.to_dict()
    actor_set = set()
    if len(target) == 0:
        abort(404)

    if 'name' in target:
        for name in set(str(target['name']).replace("|name=", ",").split(",")):
            for actor in actor_name:
                if name in actor:
                    actor_set.add(actor)
    if 'age' in target:
        age_set = set(str(target['age']).replace("|age=", ",").split(","))
        if len(actor_set) == 0:
            for actor in actor_name:
                cur = g.get_vertex_info(actor)
                if str(cur.age) in age_set:
                    actor_set.add(actor)
        else:
            for already in actor_set.copy():
                cur = g.get_vertex_info(already)
                if str(cur.age) not in age_set:
                    actor_set.remove(already)

    return jsonify({"Actors": list(actor_set)})

"""
/movies?attr={attr_value} Example: /movies?name=”Shawshank&Redemption”

Filters out all actors that don’t have “Shawshank&Redemption” in 
their name (Should allow for similar filtering for any other attribute)
"""
@app.route('/movies', methods=['GET'])
def filter_movies():
    target = request.args.to_dict()
    movie_set = set()
    if len(target) == 0:
        abort(404)

    if 'name' in target:
        for name in set(str(target['name']).replace("|name=", ",").split(",")):
            for movie in movie_name:
                if name in movie:
                    movie_set.add(movie)
    if 'year' in target:
        year_set = set(str(target['year']).replace("|year=", ",").split(","))
        if len(movie_set) == 0:
            for movie in movie_name:
                cur = g.get_vertex_info(movie)
                if str(cur.date) in year_set:
                    movie_set.add(movie)
        else:
            for already in movie_set.copy():
                cur = g.get_vertex_info(already)
                if str(cur.date) not in year_set:
                    movie_set.remove(already)
    if 'gross' in target:
        gross_set = set(str(target['gross']).replace("|gross=", ",").split(","))
        if len(movie_set) == 0:
            for movie in movie_name:
                cur = g.get_vertex_info(movie)
                if str(cur.gross) in gross_set:
                    movie_set.add(movie)
        else:
            for already in movie_set.copy():
                cur = g.get_vertex_info(already)
                if str(cur.gross) not in gross_set:
                    movie_set.remove(already)
    return jsonify({"Movies": list(movie_set)})

"""
/actors/:{actor_name} Example: /actors/Bruce_Willis

Returns the first Actor object that has name “Bruce Willis”, 
displays actor attributes and metadata
"""
@app.route('/actors/<string:given_name>', methods=['GET'])
def get_actor(given_name):
    given_name = given_name.replace("_", " ")
    for i in actor_name:
        if i.lower() == given_name.lower():
            given_name = i
            continue
    if given_name not in actor_name:
        abort(404)
    cur = g.get_vertex_info(given_name)
    if cur == None:
        abort(404)
    ret = {}
    ret['Actor Name'] = cur.name
    ret['Actor Age'] = cur.age
    ret['Actor Total Gross'] = cur.gross
    ret['Actor Wiki Page'] = cur.page
    ret['Actor Movies'] = g.get_movies_given_actor(cur.name)
    return jsonify({cur.name: ret})

"""
/movies/:{movie_name} Example: /movies/Shawshank_Redemption

Returns the first Movie object that has correct name, displays movie attributes and metadata
"""
@app.route('/movies/<string:given_name>', methods=['GET'])
def get_movie(given_name):
    given_name = given_name.replace("_", " ")
    for i in movie_name:
        if i.lower() == given_name.lower():
            given_name = i
            continue
    if given_name not in movie_name:
        abort(404)
    cur = g.get_vertex_info(given_name)
    if cur == None:
        abort(404)
    ret = {}
    ret['Movie Name'] = cur.name
    ret['Movie Box Office'] = cur.gross
    ret['Movie Year'] = cur.date
    ret['Movie Wiki Page'] = cur.page
    ret['Movie Actors'] = g.get_actors_given_movie(cur.name)
    return jsonify({cur.name: ret})

"""
Put: /actors
Leverage PUT requests to update standing content in backend
curl -i -X PUT -H "Content-Type: application/json" -d ' 
{"total_gross":500}'http://localhost:4567/api/a/actors/Bruce_Willis
"""
@app.route('/actors/<string:given_name>', methods=['PUT'])
def update_actors(given_name):
    if not request.json:
        abort(400)
    given_name = given_name.replace("_", " ")
    for i in actor_name:
        if i.lower() == given_name.lower():
            given_name = i
            continue
    if given_name not in actor_name:
        abort(404)
    cur = g.get_vertex_info(given_name)
    if cur == None:
        abort(404)

    if 'age' in request.json:
        g.update_age(given_name, request.json.get('age', cur.age))
    if 'total_gross' in request.json:
        g.update_gross(given_name, request.json.get('total_gross', cur.gross))
    if 'wiki_page' in request.json:
        g.update_page(given_name, request.json.get('wiki_page', cur.page))
    if 'name' in request.json:
        g.update_name(given_name, request.json.get('name', cur.name))
        actor_name.remove(given_name)
        actor_name.add(request.json.get('name', cur.name))

    new_cur = g.get_vertex_info(request.json.get('name', cur.name))
    if new_cur == None:
        abort(404)
    ret = {}
    ret['Actor Name'] = new_cur.name
    ret['Actor Age'] = new_cur.age
    ret['Actor Total Gross'] = new_cur.gross
    ret['Actor Wiki Page'] = new_cur.page
    ret['Actor Movies'] = g.get_movies_given_actor(new_cur.name)
    resp = jsonify({new_cur.name: ret, 'success':True})
    resp.status_code = 200
    return resp
    # return jsonify({new_cur.name: ret})

"""
/movies
Leverage PUT requests to update standing content in backend
curl -i -X PUT -H "Content-Type: application/json" -d ' {"box_office":500}' 
http://localhost:4567/api/m/movies/Shawshank_Redemption
"""
@app.route('/movies/<string:given_name>', methods=['PUT'])
def update_movies(given_name):
    if not request.json:
        abort(400)
    given_name = given_name.replace("_", " ")
    for i in movie_name:
        if i.lower() == given_name:
            given_name = i
            continue
    if given_name not in movie_name:
        abort(404)
    cur = g.get_vertex_info(given_name)
    if cur == None:
        abort(404)

    if 'date' in request.json:
        g.update_date(given_name, request.json.get('date', cur.date))
    if 'box_office' in request.json:
        g.update_gross(given_name, request.json.get('box_office', cur.gross))
    if 'wiki_page' in request.json:
        g.update_page(given_name, request.json.get('wiki_page', cur.page))
    if 'name' in request.json:
        g.update_name(given_name, request.json.get('name', cur.name))
        movie_name.remove(given_name)
        movie_name.add(request.json.get('name', cur.name))

    new_cur = g.get_vertex_info(request.json.get('name', cur.name))
    if new_cur == None:
        abort(404)
    ret = {}
    ret['Movie Name'] = new_cur.name
    ret['Movie Box Office'] = new_cur.gross
    ret['Movie Year'] = new_cur.date
    ret['Movie Wiki Page'] = new_cur.page
    ret['Movie Actors'] = g.get_actors_given_movie(new_cur.name)
    resp = jsonify({new_cur.name: ret, 'success':True})
    resp.status_code = 200
    return resp

"""
Delete:
/actors/:{actor_name}
Leverage DELETE requests to REMOVE content from backend
curl -i -X DELETE -H "Content-Type: application/json" 
{API URL}/actors/Bruce_Willis
"""
@app.route('/actors/<string:given_name>', methods=['DELETE'])
def delete_actor(given_name):
    given_name = given_name.replace("_", " ")
    for i in actor_name:
        if i.lower() == given_name.lower():
            given_name = i
            continue
    if given_name not in actor_name:
        abort(404)
    cur = g.get_vertex_info(given_name)
    if cur == None:
        abort(404)
    actor_name.remove(given_name)
    if g.delete_vertex(given_name):
        resp = jsonify(success=True)
        resp.status_code = 200
        return resp
    else: 
        abort(404)

"""
/movies/:{movie_name}
Leverage DELETE requests to REMOVE content from backend
curl -i -X DELETE -H "Content-Type: application/json" 
{API URL}/movies/Shawshank_Redemption
"""
@app.route('/movies/<string:given_name>', methods=['DELETE'])
def delete_movie(given_name):
    given_name = given_name.replace("_", " ")
    for i in movie_name:
        if i.lower() == given_name.lower():
            given_name = i
            continue
    if given_name not in movie_name:
        abort(404)
    cur = g.get_vertex_info(given_name)
    if cur == None:
        abort(404)
    movie_name.remove(given_name)
    if g.delete_vertex(given_name):
        resp = jsonify(success=True)
        resp.status_code = 200
        return resp
    else: 
        abort(404)

"""
Post:
/actors
Leverage POST requests to ADD content to backend
curl -i -X POST -H "Content-Type: application/json" 
-d'{"name":"Billy Joe"}' {API URL}/actors
"""
@app.route('/actors', methods=['POST'])
def add_actors():
    if not request.json or 'name' not in request.json:
        abort(400)
    if  'age' in request.json and type(request.json['age']) != int:
        abort(400)
    if  'total_gross' in request.json and type(request.json['total_gross']) != int:
        abort(400)
    if str(request.json.get('name')) in actor_name:
        abort(400)
    new_name = ""
    new_age = 0
    new_total_gross = 0
    new_page = ""
    new_movie = []

    if 'name' in request.json:
        new_name = str(request.json.get('name'))
        actor_name.add(new_name)

    if 'age' in request.json:
        new_age = int(request.json.get('age'))
   
    if 'total_gross' in request.json:
        new_total_gross = int(request.json.get('total_gross'))

    if 'wiki_page' in request.json:
        new_page  = str(request.json.get('wiki_page'))
    
    g.add_vertex_to_graph(new_name, new_age, new_total_gross, None, new_page, False)
    if 'movies' in request.json:
        for m in request.json.get('movies'):
            if m not in movie_name:
                continue
            cur_movie = g.get_vertex_info(m)
            if cur_movie == None:
                continue
            g.add_edge(new_name, cur_movie.name, cur_movie.gross)

    return json.dumps({'success':True}), 201, {'ContentType':'application/json'}

"""
/movies
Leverage POST requests to ADD content to backend
curl -i -X POST -H "Content-Type: application/json" 
-d'{"name":"Captain America"}' {API URL}/movies
"""
@app.route('/movies', methods=['POST'])
def add_movies():
    if not request.json or 'name' not in request.json:
        abort(400)
    if  'date' in request.json and type(request.json['date']) != int:
        abort(400)
    if  'box_office' in request.json and type(request.json['box_office']) != int:
        abort(400)
    if str(request.json.get('name')) in movie_name:
        abort(400)
    new_name = ""
    new_date = 0
    new_box_office = 0
    new_page = ""
    new_actor = []

    if 'name' in request.json:
        new_name = str(request.json.get('name'))
        movie_name.add(new_name)

    if 'date' in request.json:
        new_date = int(request.json.get('date'))
   
    if 'box_office' in request.json:
        new_box_office = int(request.json.get('box_office'))

    if 'wiki_page' in request.json:
        new_page  = str(request.json.get('wiki_page'))
    
    g.add_vertex_to_graph(new_name, None, new_box_office, new_date, new_page, True)
    if 'actors' in request.json:
        for a in request.json.get('actors'):
            if a not in actor_name:
                continue
            cur_actor = g.get_vertex_info(a)
            if cur_actor == None:
                continue
            g.add_edge(cur_actor.name, new_name, new_box_office)

    return json.dumps({'success':True}), 201, {'ContentType':'application/json'}

@app.route('/init', methods=['GET'])
def app_init():
    global g
    json_file = open('data.json')
    g = read_input(json_file)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    json_file = open('data.json')
    g = read_input(json_file)
    app.debug = True	
    app.run(host='127.0.0.1', port=config.PORT)