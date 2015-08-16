from stocked.models import *

def create_user(api, first_name='Ivan', last_name='Mitev', provider='facebook',
    provider_id='me', email='vini@abv.bg', friend_ids=[], installed_apps=[], recommended_apps=[]):

    return api.post_json('/users', {'firstName': first_name, 'lastName': last_name,
            'provider': provider, 'providerId': provider_id, 'friendIds':
            friend_ids, 'email': email,
            'installedApps': installed_apps, 'recommendedApps':
            recommended_apps}, expect_errors=True).json

def sign_in_user(api, provider_id='me', status=200):
    return api.post_json('/users/sign-in', {'providerId': provider_id},
            status=status, expect_errors=True)

def get_crawl_list(api):
    return api.get('/apps/crawl-list', expect_errors=True).json
         
def create_app(api, package):
    return api.post_json('/apps', 
            {'name': 'TestApp', 
            'url': 'test1', 
            'package': package,
            'publisher': 'test',
            'crawled': True,
            'icon': 'http://google.com/images.png', 
            'marketRating': {'rating': 3.9, 'rate_count': 1000},
            'downloadCount': {'lowRange': 1000, 'highRange': 5000},
            'categories': ['entertainment'],
            'images': ['img1.png'],
            'description': 'some description'}, expect_errors=True).json

def show_app(api, package, provider_id):
    return api.get('/apps/show/' + package + '/' + provider_id , expect_errors=True).json

def get_installed_apps(api, provider_id):
    return api.get('/apps/installed/' + provider_id, expect_errors=True).json

def create_uncrawled_app(api, package):
    return api.post_json('/apps/crawl-list',
            { 'packages': [package] }, expect_errors=True)

def update_app(api, package, name):
    return api.put_json('/apps', 
            {'name': name, 
            'url': 'test1', 
            'package': package,
            'icon': 'http://google.com/images.png', 
            'marketRating': {'rating': 3.9, 'rateCount': 1000},
            'downloadCount': {'lowRange': 1000, 'highRange': 5000},
            'categories': ['entertainment'],
            'description': 'some description'}, expect_errors=True).json


def rate_app(api, provider_id, app_package, rating):

    api.put_json('/apps/rate', {'providerId': provider_id, 
        'appPackage': app_package, 'rating': rating}, expect_errors=True)
