from webtest import TestApp
from stocked.models import *
from tests.crud_functions import *
from tests.test_case import *
import unittest
import webapp
import sure

class TestApplication(MongoTestRunner):

    def setUp(self):
        self.api = TestApp(webapp.api)
        AppCrawlList().save()

    def test_add_app(self):
        app = create_app(self.api, 'test1')
        app['_id'].should_not.eql(None) 

    def test_update_app(self):
        create_app(self.api, 'test1')
        app = update_app(self.api, 'test1', 'nigga1')
        app['name'].should.eql('nigga1')

    def test_show_app(self):
        create_app(self.api, 'test1')
        create_user(self.api)
        app = show_app(self.api, 'test1', 'me')
        app['url'].should.eql('test1')

    def test_show_rated_app(self):
        create_app(self.api, 't1')
        create_user(self.api)
        rate_app(self.api, 'me', 't1', 4.0)
        app = show_app(self.api, 't1', 'me')
        app['rating'].should.eql(4.0)

    def test_add_uncrawled_app(self):
        create_uncrawled_app(self.api, 'test1')
        create_user(self.api, installed_apps=['test1'])
        len(get_crawl_list(self.api)).should.eql(1)

    def test_recommend_apps(self):
        create_app(self.api, 'test1')
        create_app(self.api, 'test2')
        create_app(self.api, 'test3')
        create_app(self.api, 'test4')
        create_user(self.api, provider_id='me', installed_apps=['test1',
        'test2', 'test3'])
        create_user(self.api, provider_id='u1', installed_apps=['test1',
        'test2'])
        create_user(self.api, provider_id='u2', installed_apps=['test1',
        'test2', 'test3', 'test4'])

        rate_app(self.api, 'me', 'test1', 4.0)
        rate_app(self.api, 'me', 'test2', 4.0)
        rate_app(self.api, 'me', 'test3', 5.0)

        rate_app(self.api, 'u1', 'test1', 3.0)
        rate_app(self.api, 'u1', 'test2', 1.0)

        rate_app(self.api, 'u2', 'test1', 2.5)
        rate_app(self.api, 'u2', 'test2', 5.0)
        rate_app(self.api, 'u2', 'test3', 4.0)
        rate_app(self.api, 'u2', 'test4', 5.0)

        recommended_apps = self.api.get('/apps/recommend/me').json
        recommended_apps[0]['appPackage'].should.eql('test4')

    def test_add_not_installed_apps_when_not_enough_to_recommend(self):

        create_app(self.api, 'test1')
        create_app(self.api, 'test2')
        create_app(self.api, 'test3')
        create_app(self.api, 'test4')
        create_app(self.api, 'a1')
        create_app(self.api, 'a2')
        create_user(self.api, provider_id='me', installed_apps=['test1',
        'test2', 'test3', 'a1'])
        create_user(self.api, provider_id='u1', installed_apps=['test1',
        'test2'])
        create_user(self.api, provider_id='u2', installed_apps=['test1',
        'test2', 'test3', 'test4'])

        rate_app(self.api, 'me', 'test1', 4.0)
        rate_app(self.api, 'me', 'test2', 4.0)
        rate_app(self.api, 'me', 'test3', 5.0)

        rate_app(self.api, 'u1', 'test1', 3.0)
        rate_app(self.api, 'u1', 'test2', 1.0)

        rate_app(self.api, 'u2', 'test1', 2.5)
        rate_app(self.api, 'u2', 'test2', 5.0)
        rate_app(self.api, 'u2', 'test3', 4.0)
        rate_app(self.api, 'u2', 'test4', 5.0)

        recommended_apps = self.api.get('/apps/recommend/me').json
        len(recommended_apps).should.eql(2)

    def test_add_apps_when_not_enough_to_recommend(self):
        create_app(self.api, 'test1')
        create_app(self.api, 'test2')
        create_app(self.api, 'test3')
        create_app(self.api, 'test4')
        installed_apps=['test1', 'test2', 'test3']
        for i in range(0, 20):
            create_app(self.api, 'a' + str(i))
            installed_apps.extend('a' + str(i))
        create_user(self.api, provider_id='me', installed_apps=installed_apps)
        create_user(self.api, provider_id='u1', installed_apps=['test1',
        'test2'])
        create_user(self.api, provider_id='u2', installed_apps=['test1',
        'test2', 'test3', 'test4'])

        rate_app(self.api, 'me', 'test1', 4.0)
        rate_app(self.api, 'me', 'test2', 4.0)
        rate_app(self.api, 'me', 'test3', 5.0)

        rate_app(self.api, 'u1', 'test1', 3.0)
        rate_app(self.api, 'u1', 'test2', 1.0)

        rate_app(self.api, 'u2', 'test1', 2.5)
        rate_app(self.api, 'u2', 'test2', 5.0)
        rate_app(self.api, 'u2', 'test3', 4.0)
        rate_app(self.api, 'u2', 'test4', 5.0)

        recommended_apps = self.api.get('/apps/recommend/me').json
        len(recommended_apps).should.eql(20)


    def test_installed_apps(self):
        create_app(self.api, 't1')
        create_app(self.api, 't2')
        create_user(self.api, installed_apps=['t1', 't2'])
        len(get_installed_apps(self.api, 'me')).should.eql(2)

    def test_installed_apps_should_be_added_to_crawl_list(self):
        create_user(self.api, installed_apps=['t1'])
        crawl_list = AppCrawlList.objects.get()
        len(get_crawl_list(self.api)).should.eql(1)
