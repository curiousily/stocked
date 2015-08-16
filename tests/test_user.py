from webtest import TestApp
from stocked.models import *
from tests.crud_functions import *
from tests.test_case import *
import unittest
import webapp
import sure

class TestUser(MongoTestRunner):

    def setUp(self):
        self.api = TestApp(webapp.api)
        AppCrawlList([]).save()

    def test_create_user(self):
        user = create_user(self.api)
        user['_id'].should_not.eql(None)

    def test_sing_in_user(self):
        create_user(self.api, provider_id='me', first_name='Ivan')
        user = sign_in_user(self.api, provider_id='me').json
        user['firstName'].should.eql('Ivan')

    def test_add_new_user(self):
        sign_in_user(self.api, provider_id='me',
                status=401).status_int.should.eql(401)
        create_user(self.api, provider_id='me', first_name='Ivan')
        user = sign_in_user(self.api, provider_id='me').json
        user['firstName'].should.eql('Ivan')

    def test_register_user_with_friends(self):
        create_user(self.api, provider_id='id1')
        u = create_user(self.api, friend_ids=['id1'])
        len(u['friends']).should.eql(1)

    def test_user_mutual_friendship(self):
        create_user(self.api, provider_id='id1')
        create_user(self.api, friend_ids=['id1'])
        u = self.api.get('/users/' + 'id1').json
        len(u['friends']).should.eql(1)

    def test_register_user_with_installed_apps(self):
        create_app(self.api, 'com.app.example')
        u = create_user(self.api, installed_apps=['com.app.example'])
        len(u['installed_apps']).should.eql(1)

    def test_update_installed_apps(self):
        create_app(self.api, 'com.example')
        create_user(self.api, provider_id='id1', installed_apps=['com.example'])
        self.api.put_json('/users/' + 'id1' + '/update-app-list', 
                {'installedApps':['com.app']})
        crawl_list = get_crawl_list(self.api)
        crawl_list.should.eql(['com.app'])

    def test_remove_installed_apps_from_recommended(self):

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

        self.api.put_json('/users/' + 'me' + '/update-app-list', 
                {'installedApps':['test4']})
        recommended_apps = self.api.get('/apps/recommend/me').json
        len(recommended_apps).should.eql(0)
