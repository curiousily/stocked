from bottle import *
from stocked.models import *
from stocked.recommender import Recommender
from stocked.json_handlers import *
import requests
import logging
import json
import jsonpickle
import random
from jsonpickle.handlers import *

MIN_RECOMMENDED_APPS=20

BaseResponse.default_content_type = 'application/json; charset=UTF-8'
logging.basicConfig(level=logging.DEBUG,
                    format='%(process)s %(levelname)s %(message)s')

api = Bottle()
registry.register(User, UserHandler)

@api.post('/users')
def create_user():
    json = request.json
    friends = User.objects(provider_id__in=json['friendIds'])
    crawl_list = AppCrawlList.objects.get()
    apps = []
    for app_package in json['installedApps']:
        if App.objects(package=app_package).count() > 0:
            app = App.objects(package=app_package).get()
        else:
            crawl_list.apps.append(app_package)
            app = App(crawled=False,
                name='', package=app_package, publisher=None, icon_url='',
                categories=[], url='', market_rating=None, download_count=None,
                description='', images=[])
            app.save()
        apps.append(app)

    crawl_list.save()
    user = User(json['firstName'], json['lastName'], json['email'], json['provider'],
            json['providerId'], friends, apps, [])
    user.save()
    for friend in friends:
        friend.friends.append(user)
        friend.save()
    return user.to_json()

@api.post('/users/sign-in')
def sign_in_user():
    json = request.json
    users = User.objects(provider_id=json['providerId'])
    if(len(users) > 0):
        return jsonpickle.encode(users.get(), unpicklable=False)
    else:
        response.status = 401
        return jsonpickle.encode({'errors': ['Unauthorized user']})

@api.delete('/users')
def delete_user():
    user_id = request.json['user_id']
    user = User.objects.get(id=user_id)
    user.delete()

@api.get('/users/:provider_id')
def find_user_by_id(provider_id):
    return User.objects.get(provider_id=provider_id).to_json()

@api.put('/users/:provider_id/update-app-list')
def update_user_app_list(provider_id):
    u = User.objects.get(provider_id=provider_id)
    installed_apps = set(request.json['installedApps'])
    crawl_list = AppCrawlList.objects.get()
    for app_package in installed_apps:
        if len(App.objects(package=app_package)) == 0:
            crawl_list.apps.append(app_package)
            app = App(crawled=False,
                name='', package=app_package, publisher=None, icon_url='',
                categories=[], url='', market_rating=None, download_count=None,
                description='', images=[])
            app.save()
        else:
            app = App.objects.get(package=app_package)
        u.installed_apps.append(app)
        _remove_from_recommended_apps(u, app_package)
    crawl_list.save()
    u.save()
    return u.to_json()

def _remove_from_recommended_apps(user, app_package):
    new_recommended_apps = []
    for index, recommended_app in user.recommended_apps:
        if app_package != recommended_app.package:
            new_recommended_apps.append(recommended_app)
    user.recommended_apps = []
    for recommended_app in new_recommended_apps:
        user.recommended_apps.append(recommended_app)

@api.get('/apps/crawl-list')
def get_crawl_list():
    crawl_list = AppCrawlList.objects.get()
    app_list = crawl_list.apps
    return json.dumps(app_list)

@api.post('/apps')
def add_app():
    json = request.json
    market_rating = MarketRating(rating=json['marketRating']['rating'],
            rate_count=json['marketRating']['rateCount'])
    download_count = DownloadCount(low_range=json['downloadCount']['lowRange'],
            high_range=json['downloadCount']['highRange'])
    app_categories = json['categories']
    _save_new_categories(app_categories)
    categories = Category.objects(name__in=app_categories)
    Publisher.objects(name=json['publisher']).update_one(set__name=json['publisher'],
            upsert=True)
    publisher = Publisher.objects.get(name=json['publisher'])
    app = App(name=json['name'], categories=categories, publisher=publisher, url=json['url'],
            package=json['package'], crawled=json['crawled'],
            icon_url=json['icon_url'], description=json['description'], 
            images=json['images'], market_rating=market_rating,
            download_count=download_count)
    app.save()
    return app.to_json()

@api.post('/apps/crawl-list')
def add_app_to_crawl_list():
    json = request.json
    crawl_list = AppCrawlList.objects.get()
    packages = set(json['packages'])
    for package in packages:
        app = App(crawled=False,
                name='', package=package, publisher=None, icon_url='',
                categories=[], url='', market_rating=None, download_count=None,
                description='', images=[])
        app.save()
    crawl_list.apps.extend(packages)
    crawl_list.save()

def _save_new_categories(app_categories):
    for category in app_categories:
        Category.objects(name=category).update_one(set__name=category,
            upsert=True)

@api.put('/apps')
def update_app():
    json = request.json
    print(json)
    package = json['package']
    app = App.objects.get(package=package)
    if(has_json_key('name')):
        app.name = json['name']
    if(has_json_key('url')):
        app.url = json['url']
    if(has_json_key('icon_url')):
        app.icon_url = json['icon_url']
    if(has_json_key('publisher')):
        publisher, _ = Publisher.objects.get_or_create(name=json['publisher'])
        app.publisher = publisher
    if(has_json_key('description')):
        app.description = json['description']
    if(has_json_key('crawled')):
        app.crawled = json['crawled']
    if(has_json_key('images')):
        app.images = json['images']
    if(has_json_key('categories')):
        app_categories = json['categories']
        _save_new_categories(app_categories)
        categories = Category.objects(name__in=app_categories)
        app.categories = categories
    if(has_json_key('marketRating')):
        app.market_rating = MarketRating(rating=json['marketRating']['rating'],
            rate_count=json['marketRating']['rateCount'])
    if(has_json_key('downloadCount')):
        app.download_count = DownloadCount(low_range=json['downloadCount']['lowRange'],
            high_range=json['downloadCount']['highRange'])
    app.save()
    _remove_from_crawl_list(app.package)
    return app.to_json()

def _remove_from_crawl_list(app_package):
    crawl_list = AppCrawlList.objects.get()
    if app_package in crawl_list.apps:
        crawl_list.apps.remove(app_package)
    crawl_list.save()

def has_json_key(key):
    return key in request.json

@api.put('/apps/rate')
def rate_app():
    provider_id = request.json['providerId']
    app_package = request.json['appPackage']
    rating = request.json['rating']
    user = User.objects.get(provider_id=provider_id)
    app = App.objects.get(package=app_package)
    app.rate(user, rating)
    app.save()

@api.get('/apps/recommend/:provider_id')
def recommend_apps(provider_id):
    random.seed()
    user = User.objects.get(provider_id=provider_id)
    if len(user.recommended_apps) < MIN_RECOMMENDED_APPS:
        user.recommended_apps = []
        recommender = Recommender()
        recommendations = recommender.get_recommendations(User.objects(), user)
        recommended_apps = [recommendation[1] for recommendation in recommendations]
        if len(recommended_apps) < MIN_RECOMMENDED_APPS:
            recommended_apps.extend(add_unused_apps(recommended_apps, user))
        for recommended_app in recommended_apps:
            user.recommended_apps.append(recommended_app)
        user.save()
    result_packages = [recommendation.package for recommendation in
            user.recommended_apps]
    apps = list(App.objects(package__in=result_packages))
    registry.register(App, AppListItemHandler)
    return jsonpickle.encode(apps, unpicklable=False)

def add_unused_apps(recommended_apps, user):
    apps = recommended_apps
    used_packages = create_used_packages(apps, user)
    not_used_apps = App.objects(package__not__in=used_packages)
    available_app_count = len(not_used_apps)
    apps_to_add = MIN_RECOMMENDED_APPS  - len(apps)
    if apps_to_add > available_app_count:
        apps.extend(not_used_apps)
    else:
        indecis = create_app_indecis(available_app_count, apps_to_add)
        for index in indecis:
            apps.append(not_used_apps[index])
    return apps

def create_used_packages(recommended_apps, user):
    used_packages = [app.package for app in recommended_apps]
    used_packages.extend([app.package for app in user.installed_apps])
    return used_packages

def create_app_indecis(available_app_count, apps_to_add):
    sequence = list(range(0, available_app_count))
    random.shuffle(sequence)
    return sequence[:apps_to_add]
    

@api.get('/apps/installed/:provider_id')
def installed_apps(provider_id):
    user = User.objects.get(provider_id=provider_id)
    apps = []
    for app in user.installed_apps:
        if app.crawled:
            apps.append(app)
    registry.register(App, AppListItemHandler)
    return jsonpickle.encode(apps, unpicklable=False)

@api.get('/apps/show/:package/:provider_id')
def show_app(package, provider_id):
    registry.register(App, AppDetailHandler)
    app = App.objects.get(package=package)
    res = jsonpickle.encode(app, unpicklable=False)
    if not provider_id == None:
        user = User.objects.get(provider_id=provider_id)
        app_rating = user.rating_of(app)
        decoded = jsonpickle.decode(res)
        decoded['rating'] = app_rating
    return jsonpickle.encode(decoded, unpicklable=False)

app = Bottle()
app.mount('api/v1/', api)
if __name__ == '__main__':
    run(app, debug=True, reloader=True)
