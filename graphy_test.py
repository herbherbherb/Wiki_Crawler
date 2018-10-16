import unittest
from unittest import TestCase
from model.graphy import myGraph
from model.Scraper import Actor, Movie

class TestGraphyMethods(unittest.TestCase):
    print("Running Graph Structure Test Cases: ")
    def initlize(self):
        g = myGraph()
        actor1 = Actor(actor_name="Herbert1", actor_age="(aged 21)", page="https://en.wikipedia.org/wiki/Herbert_Wang")
        actor2 = Actor(actor_name="Herbert2", actor_age="(aged 25)", page="https://en.wikipedia.org/wiki/Herbert_Wang2")
        movie1 = Movie(name="My first movie", gross=13124.0, date="2018-10-7", \
                                actors=["Herbert1", "Herbert2"], page="wiki_Herbert")
        movie2 = Movie(name="My second movie", gross=424232.0, date="2018-1-27", \
                                actors=["Herbert2"], page="wiki_Herbert2")

        g.add_vertex_to_graph(actor1['actor_name'], actor1['actor_age'], None, None, actor1['page'], False)
        g.add_vertex_to_graph(actor2['actor_name'], actor2['actor_age'], None, None, actor2['page'], False)
        g.add_vertex_to_graph(movie1['name'], None, movie1['gross'], movie1['date'], movie1['page'], True)
        g.add_vertex_to_graph(movie2['name'], None, movie2['gross'], movie2['date'], movie2['page'], True)
        g.add_edge(actor1['actor_name'], movie1['name'], movie1['gross'])
        g.add_edge(actor2['actor_name'], movie1['name'], movie1['gross'])
        g.add_edge(actor2['actor_name'], movie2['name'], movie2['gross'])
        return g
    def test_add_vertex_to_graph(self):
        g = self.initlize()
        self.assertEqual("Herbert1", g.get_vertex_info("Herbert1").name)
        self.assertEqual("(aged 21)", g.get_vertex_info("Herbert1").age)
        self.assertEqual("https://en.wikipedia.org/wiki/Herbert_Wang", g.get_vertex_info("Herbert1").page)
        self.assertIsNone(g.get_vertex_info("Herbert1").date)
        self.assertIsNone(g.get_vertex_info("Herbert1").gross)
        self.assertEqual("My first movie", g.get_vertex_info("My first movie").name)
        self.assertIsNone(g.get_vertex_info("My first movie").age)
        self.assertEqual(13124.0, g.get_vertex_info("My first movie").gross)
        self.assertEqual("2018-10-7", g.get_vertex_info("My first movie").date)
        self.assertEqual("wiki_Herbert", g.get_vertex_info("My first movie").page)

    def test_get_actors_given_movie(self):
        g = self.initlize()
        ret = g.get_actors_given_movie("My first movie")
        self.assertTrue("Herbert1" in ret)
        self.assertTrue("Herbert2" in ret)
        self.assertEqual(len(ret), 2)
        self.assertFalse("Herbert12312" in ret)

    def test_get_movies_given_actor(self):
        g = self.initlize()
        ret = g.get_movies_given_actor("Herbert2")
        self.assertTrue("My first movie" in ret)
        self.assertTrue("My second movie" in ret)
        self.assertEqual(len(ret), 2)
        self.assertFalse("My third movie" in ret)

    def test_get_all_movie_name(self):
        g = self.initlize()
        ret = g.get_all_movie_name()
        self.assertEqual(len(ret), 2)
        self.assertTrue("My first movie" in ret)
        self.assertTrue("My second movie" in ret)
        self.assertFalse("My third movie" in ret)

    def test_get_all_actor_name(self):
        g = self.initlize()
        ret = g.get_all_actor_name()
        self.assertEqual(len(ret), 2)
        self.assertTrue("Herbert1" in ret)
        self.assertTrue("Herbert2" in ret)
        self.assertFalse("Herbert3" in ret)

    def test_get_vertex_info(self):
        g = self.initlize()
        self.assertEqual("Herbert2", g.get_vertex_info("Herbert2").name)
        self.assertEqual("(aged 25)", g.get_vertex_info("Herbert2").age)
        self.assertEqual("https://en.wikipedia.org/wiki/Herbert_Wang2", g.get_vertex_info("Herbert2").page)
        self.assertIsNone(g.get_vertex_info("Herbert2").date)
        self.assertIsNone(g.get_vertex_info("Herbert2").gross)
        self.assertEqual("My second movie", g.get_vertex_info("My second movie").name)
        self.assertIsNone(g.get_vertex_info("My second movie").age)
        self.assertEqual(424232.0, g.get_vertex_info("My second movie").gross)
        self.assertEqual("2018-1-27", g.get_vertex_info("My second movie").date)
        self.assertEqual("wiki_Herbert2", g.get_vertex_info("My second movie").page) 
        
    def test_get_vertices(self):
        g = self.initlize()
        ret = g.get_vertices()
        self.assertEqual(len(ret), 4)
        self.assertTrue("Herbert1" in ret)
        self.assertTrue("Herbert2" in ret)
        self.assertTrue("My first movie" in ret)
        self.assertTrue("My second movie" in ret)

    def test_get_all_movie_given_year(self):
        g = self.initlize()
        ret = g.get_all_movie_given_year("2018")
        self.assertEqual(len(ret), 2)
        self.assertTrue("My first movie" in ret)
        self.assertTrue("My second movie" in ret)

    def test_get_all_actor_given_year(self):
        g = self.initlize()
        ret = g.get_all_actor_given_year("2018")
        self.assertEqual(len(ret), 2)
        self.assertTrue("Herbert1" in ret)
        self.assertTrue("Herbert2" in ret)

    def test_get_movie_gross(self):
        g = self.initlize()
        ret = g.get_movie_gross("My first movie")
        self.assertEqual("My first movie's Gross: $13124.0", ret)
        ret = g.get_movie_gross("My second movie")
        self.assertEqual("My second movie's Gross: $424232.0", ret)

    def test_get_top_oldest(self):
        g = self.initlize()
        ret = g.get_top_oldest(1)
        self.assertEqual(len(ret), 1)
        self.assertEqual("Herbert2", ret[0][0])
        self.assertEqual(25, ret[0][1])
        ret = g.get_top_oldest(2)
        self.assertEqual(len(ret), 2)
        self.assertEqual("Herbert2", ret[0][0])
        self.assertEqual(25, ret[0][1])
        self.assertEqual("Herbert1", ret[1][0])
        self.assertEqual(21, ret[1][1])

    def test_get_topK(self):
        g = self.initlize()
        ret = g.get_topK(1)
        self.assertEqual(len(ret), 1)
        self.assertEqual("Herbert2", ret[0][0])
        self.assertEqual("$437356.0", ret[0][1])
        ret = g.get_topK(2)
        self.assertEqual(len(ret), 2)
        self.assertEqual("Herbert2", ret[0][0])
        self.assertEqual("$437356.0", ret[0][1])
        self.assertEqual("Herbert1", ret[1][0])
        self.assertEqual("$13124.0", ret[1][1])

    def test_get_movie_info(self):
        g = self.initlize()
        ret = g.get_movie_info("My first movie")
        self.assertEqual(ret, "Movie Name: My first movie\nGross: $13124.0\nRelease Date: 2018-10-7\nWiki Page: wiki_Herbert")
        ret = g.get_movie_info("My second movie")
        self.assertEqual(ret, "Movie Name: My second movie\nGross: $424232.0\nRelease Date: 2018-1-27\nWiki Page: wiki_Herbert2")
        ret = g.get_movie_info("Wrong movie")
        self.assertNotEqual(ret, "Movie Name: My second movie\nGross: $424232.0\nRelease Date: 2018-1-27\nWiki Page: wiki_Herbert2")
        self.assertEqual(ret, "No such movie found!")

    def test_get_actor_info(self):
        g = self.initlize()
        ret = g.get_actor_info("Herbert1")
        self.assertEqual(ret, "Actor Name: Herbert1\nAge: (aged 21)\nWiki Page: https://en.wikipedia.org/wiki/Herbert_Wang")
        ret = g.get_actor_info("Herbert2")
        self.assertEqual(ret, "Actor Name: Herbert2\nAge: (aged 25)\nWiki Page: https://en.wikipedia.org/wiki/Herbert_Wang2")
        ret = g.get_actor_info("Wrong actor")
        self.assertNotEqual(ret, "Actor Name: Herbert2\nAge: (aged 25)\nWiki Page: https://en.wikipedia.org/wiki/Herbert_Wang2")
        self.assertEqual(ret, "No such actor found!")
    
    def test_get_hub_actors(self):
        g = self.initlize()
        actor3 = Actor(actor_name="Herbert3", actor_age="(aged 40)", page="https://en.wikipedia.org/wiki/Herbert_Wang3")
        movie3 = Movie(name="My third movie", gross=93334.0, date="2018-09-14", \
                                actors=["Herbert3"], page="wiki_Herbert")
        g.add_vertex_to_graph(actor3['actor_name'], actor3['actor_age'], None, None, actor3['page'], False)
        g.add_vertex_to_graph(movie3['name'], None, movie3['gross'], movie3['date'], movie3['page'], True)
        g.add_edge(actor3['actor_name'], movie3['name'], movie3['gross'])
        g.add_edge("Herbert2", movie3['name'], movie3['gross'])
        self.assertEqual("Herbert2 with largest connection of 2\n", g.get_hub_actors())

    def test_delete_vertex(self):
        g = self.initlize()
        actor3 = Actor(actor_name="Herbert3", actor_age="(aged 40)", page="https://en.wikipedia.org/wiki/Herbert_Wang3")
        movie3 = Movie(name="My third movie", gross=93334.0, date="2018-09-14", \
                                actors=["Herbert3"], page="wiki_Herbert")
        g.add_vertex_to_graph(actor3['actor_name'], actor3['actor_age'], None, None, actor3['page'], False)
        g.add_vertex_to_graph(movie3['name'], None, movie3['gross'], movie3['date'], movie3['page'], True)
        g.add_edge(actor3['actor_name'], movie3['name'], movie3['gross'])
        g.add_edge("Herbert2", movie3['name'], movie3['gross'])
        g.delete_vertex("Herbert2")
        self.assertTrue("Herbert2" not in g.get_actors_given_movie("My third movie"))
        self.assertTrue("Herbert2" not in g.get_actors_given_movie("My second movie"))
        self.assertTrue("Herbert2" not in g.get_actors_given_movie("My first movie"))
        g.add_edge("Herbert1", movie3['name'], movie3['gross'])
        g.delete_vertex("My third movie")
        self.assertTrue("My third movie" not in g.get_movies_given_actor("Herbert1"))

if __name__ == '__main__':
    unittest.main()