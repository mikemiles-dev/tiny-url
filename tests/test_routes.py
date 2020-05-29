# project/test_basic.py


import json
import unittest

from src.tiny import app


class BasicTests(unittest.TestCase):

    ############################
    #   setup and teardown     #
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()

        self.assertEqual(app.debug, False)

    ###############
    #    tests    #
    ###############

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

    def test_add(self):
        """Test we can add, get short link, and get redirect"""
        short_link = "jR"
        response = self.app.post('/add/',
                                 data={"url": "www.example.com"})
        add_resp = {"status": "success",
                    "stats_url": "http://localhost:5000/stats/jR",
                    "url": "http://localhost:5000/jR"}
        self.assertEqual(json.loads(response.data), add_resp)
        self.assertEqual(response.status_code, 200)
        response = self.app.get("/{}".format(short_link),
                                follow_redirects=False)
        self.assertEqual(response.status_code, 308)

    def test_add_custom(self):
        """Test we can add with custom  short link, and get redirect

        Also tests again to make sure we get error.
        """
        response = self.app.post('/add/',
                                 data={"url": "www.example.com",
                                       "custom": "foo"})
        self.assertEqual(response.status_code, 200)
        short_link = response.data.split(b'http://localhost:5000/')[-1]
        response = self.app.get("/{}".format(short_link),
                                follow_redirects=False)
        self.assertEqual(response.status_code, 308)
        response = self.app.post('/add/',
                                 data={"url": "www.example.com",
                                       "custom": "foo"})
        self.assertEqual(response.data,
                         b'{"error": "Custom short link exists"}')

    #  Todo add more tests for error conditions
