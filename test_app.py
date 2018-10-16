import os
import tempfile
import pytest
from app import app
import unittest
import unittest
from flask import Flask
from flask_testing import TestCase
import json
"""
Sources:
https://pythonhosted.org/Flask-Testing/ 
"""

class FlaskrTestCase(unittest.TestCase):
	print("Running API Test Cases: ")
	def create_app(self):
		app = Flask(__name__)
		app.config['TESTING'] = True
		# Default port is 5000
		app.config['LIVESERVER_PORT'] = 5001
		# Default timeout is 5 seconds
		app.config['LIVESERVER_TIMEOUT'] = 10
		self.app = app.test_client()
		return app

	def test_filter_actor(self):
		data = {'name': 'Mark|name=Chris', 'age': '35|age=45|age=73'}
		with app.test_client() as c:
			c.get('/init')
			response = c.get('/actors', query_string = data)
			result = json.loads(response.data)
			self.assertIn("Chris Tucker", result['Actors'])
			self.assertIn("Christopher Walken", result['Actors'])
			self.assertIn("Hayden Christensen", result['Actors'])

	def test_filter_movies(self):
		with app.test_client() as c:
			c.get('/init')
			data1 = {'name': 'The|name=Fine|name=September', 'year': '2015|year=2016|year=1981|year=1987', 
			'gross': 486434}
			response = c.get('/movies', query_string = data1)
			result = json.loads(response.data)
			self.assertIn("September", result['Movies'])
			data2 = {'name': 'The|name=Fine|name=September', 'year': '2015|year=2016|year=1981|year=1987'}
			response = c.get('/movies', query_string = data2)
			result = json.loads(response.data)
			self.assertIn("September", result['Movies'])
			self.assertIn("The Great Muppet Caper", result['Movies'])
			self.assertIn("So Fine", result['Movies'])
			self.assertIn("Zorro, The Gay Blade", result['Movies'])

	def test_get_actor(self):
		with app.test_client() as c:
			c.get('/init')
			response = c.get('/actors/Betty Buckley')
			result = json.loads(response.data)
			answer = {'Actor Age': 69, 'Actor Movies': ['Split'], 'Actor Name': 'Betty Buckley', 'Actor Total Gross': 193, 'Actor Wiki Page': ''}
			self.assertEqual(answer, result['Betty Buckley'])
			response = c.get('/actors/Betty_Buckley')
			result = json.loads(response.data)
			answer = {'Actor Age': 69, 'Actor Movies': ['Split'], 'Actor Name': 'Betty Buckley', 'Actor Total Gross': 193, 'Actor Wiki Page': ''}
			self.assertEqual(answer, result['Betty Buckley'])

	def test_get_movie(self):
		with app.test_client() as c:
			c.get('/init')
			response = c.get('/movies/Blind Date')
			result = json.loads(response.data)['Blind Date']
			self.assertIn('Kim Basinger', result['Movie Actors'])
			self.assertIn('Bruce Willis', result['Movie Actors'])
			self.assertIn('John Larroquette', result['Movie Actors'])
			self.assertEqual(39, result['Movie Box Office'])
			self.assertEqual(1987, result['Movie Year'])

			response = c.get('/movies/Blind_Date')
			result = json.loads(response.data)['Blind Date']
			self.assertIn('Kim Basinger', result['Movie Actors'])
			self.assertIn('Bruce Willis', result['Movie Actors'])
			self.assertIn('John Larroquette', result['Movie Actors'])
			self.assertEqual(39, result['Movie Box Office'])
			self.assertEqual(1987, result['Movie Year'])

	def test_update_actors(self):
		headers = {'content-type': 'application/json'}
		with app.test_client() as c:
			data1 = {'age': 27111, 'total_gross': 2414124, 'wiki_page': 'https://en.wikipedia.org/wiki/Bruce_Willis'}
			c.get('/init')
			response = c.put('/actors/Bruce Willis', data=json.dumps(data1), headers=headers)
			result = json.loads(response.data)['Bruce Willis']
			self.assertEqual(27111, result['Actor Age'])
			self.assertEqual(2414124, result['Actor Total Gross'])
			self.assertEqual("https://en.wikipedia.org/wiki/Bruce_Willis", result['Actor Wiki Page'])

			data2 = {'name': 'Bruce Willis1', 'age': 27111, 'total_gross': 2414124, 'wiki_page': 'https://en.wikipedia.org/wiki/Bruce_Willis'}
			response = c.put('/actors/Bruce Willis', data=json.dumps(data2), headers=headers)
			result = json.loads(response.data)['Bruce Willis1']
			self.assertEqual('Bruce Willis1', result['Actor Name'])

			response = c.get('/actors/Bruce Willis')
			self.assertEqual(str(response), "<Response streamed [404 NOT FOUND]>")

	def test_update_movies(self):
		headers = {'content-type': 'application/json'}
		with app.test_client() as c:
			data1 = {'date': 2018, 'box_office': 1999, 'wiki_page': 'https://en.wikipedia.org/wiki/Blind_Date_(1987_film)'}
			c.get('/init')
			response = c.put('/movies/Blind_Date', data=json.dumps(data1), headers=headers)
			result = json.loads(response.data)['Blind Date']
			self.assertEqual(1999, result['Movie Box Office'])
			self.assertEqual(2018, result['Movie Year'])
			self.assertIn('Kim Basinger', result['Movie Actors'])
			self.assertIn('John Larroquette', result['Movie Actors'])

			data2 = {'name': 'Blind Date12', 'date': 2018, 'box_office': 1999, 'wiki_page': 'https://en.wikipedia.org/wiki/Blind_Date_(1987_film)'}
			response = c.put('/movies/Blind_Date', data=json.dumps(data2), headers=headers)
			result = json.loads(response.data)['Blind Date12']

			self.assertEqual(1999, result['Movie Box Office'])
			self.assertEqual('Blind Date12', result['Movie Name'])
			self.assertEqual(2018, result['Movie Year'])
			self.assertIn('Kim Basinger', result['Movie Actors'])
			self.assertIn('John Larroquette', result['Movie Actors'])

			response = c.get('/movies/Blind_Date')
			self.assertEqual(str(response), "<Response streamed [404 NOT FOUND]>")

	def test_delete_actor(self):
		headers = {'content-type': 'application/json'}
		with app.test_client() as c:
			c.get('/init')
			response = c.get('/actors/Bruce_Willis')
			result = json.loads(response.data)['Bruce Willis']
			self.assertEqual(61, result['Actor Age'])
			self.assertEqual(562709189, result['Actor Total Gross'])
			response = c.delete('/actors/Bruce_Willis')
			self.assertEqual(str(response), "<Response streamed [200 OK]>")

			response = c.get('/actors/Bruce_Willis')
			self.assertEqual(str(response), "<Response streamed [404 NOT FOUND]>")

	def test_delete_movie(self):
		headers = {'content-type': 'application/json'}
		with app.test_client() as c:
			c.get('/init')
			response = c.get('/movies/Blind Date')
			result = json.loads(response.data)['Blind Date']
			self.assertIn('Kim Basinger', result['Movie Actors'])
			self.assertIn('Bruce Willis', result['Movie Actors'])
			self.assertIn('John Larroquette', result['Movie Actors'])
			self.assertEqual(39, result['Movie Box Office'])
			self.assertEqual(1987, result['Movie Year'])

			response = c.delete('/movies/Blind Date')
			self.assertEqual(str(response), "<Response streamed [200 OK]>")

			response = c.get('/movies/Blind Date')
			self.assertEqual(str(response), "<Response streamed [404 NOT FOUND]>")

	def test_add_actors(self):
		headers = {'content-type': 'application/json'}
		with app.test_client() as c:
			c.get('/init')

			data1 = {'age': 21, 
				'total_gross': 99999, 'wiki_page': 'https://en.wikipedia.org/wiki/Herbert_Wang', 
				'movies': ["Blind Date", "The Verdict"]}
			response = c.post('/actors', data=json.dumps(data1), headers=headers)
			self.assertEqual(str(response), "<Response streamed [400 BAD REQUEST]>")

			data2 = {'name': 'Herbert Wang', 'age': 21, 
				'total_gross': 99999, 'wiki_page': 'https://en.wikipedia.org/wiki/Herbert_Wang', 
				'movies': ["Blind Date", "The Verdict"]}
			response = c.post('/actors', data=json.dumps(data2), headers=headers)
			self.assertEqual(str(response), "<Response streamed [201 CREATED]>")

			response = c.get('/actors/Herbert Wang')
			result = json.loads(response.data)['Herbert Wang']
			answer = {'Actor Age': 21, 'Actor Movies': ['Blind Date', 'The Verdict'], 'Actor Name': 'Herbert Wang', 'Actor Total Gross': 99999, 'Actor Wiki Page': 'https://en.wikipedia.org/wiki/Herbert_Wang'}
			self.assertEqual(answer, result)

			response = c.get('/movies/Blind Date')
			result = json.loads(response.data)['Blind Date']
			self.assertIn('Herbert Wang', result['Movie Actors'])

	def test_add_movies(self):
		headers = {'content-type': 'application/json'}
		with app.test_client() as c:
			c.get('/init')

			data1 = {'date': 2018, 
				'box_office': 123456, 'wiki_page': 'https://en.wikipedia.org/wiki/Fun_Movie_by_Herbert_Wang', 
				'actors': ["Herbert Wang", "Betty Buckley"]}
			response = c.post('/movies', data=json.dumps(data1), headers=headers)
			self.assertEqual(str(response), "<Response streamed [400 BAD REQUEST]>")

			data2 = {'name': 'Fun Movie by Herbert Wang', 'date': 2018, 
				'box_office': 123456, 'wiki_page': 'https://en.wikipedia.org/wiki/Fun_Movie_by_Herbert_Wang', 
				'actors': ["Herbert Wang", "Betty Buckley"]}
			response = c.post('/movies', data=json.dumps(data2), headers=headers)
			self.assertEqual(str(response), "<Response streamed [201 CREATED]>")


			response = c.get('/movies/Fun Movie by Herbert Wang')
			result = json.loads(response.data)['Fun Movie by Herbert Wang']
			answer = {'Movie Actors': ['Betty Buckley'], 'Movie Box Office': 123456, 'Movie Name': 'Fun Movie by Herbert Wang', 'Movie Wiki Page': 'https://en.wikipedia.org/wiki/Fun_Movie_by_Herbert_Wang', 'Movie Year': 2018}
			
			self.assertIn('Betty Buckley', result['Movie Actors'])
			self.assertEqual(123456, result['Movie Box Office'])
			self.assertEqual(2018, result['Movie Year'])

			response = c.get('/actors/Betty Buckley')
			result = json.loads(response.data)['Betty Buckley']
			self.assertIn('Fun Movie by Herbert Wang', result['Actor Movies'])

if __name__ == '__main__':
	unittest.main()