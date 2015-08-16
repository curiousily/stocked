from behave import *
from webtest import TestApp
import sure
import requests
import json
from stocked.models import User, App, Category
from stocked.recommender import Recommender
import webapp

@given('an app')
def step(context):
    pass

@when('I enter the app installs')
def step(context):
    context.app.add_installs(1000)
    context.app.add_installs(2000)

@then('I should see average daily installs')
def step(context):
    context.app.average_daily_installs().should.be.eql(1500)

@then('total installs')
def step(context):
    context.app.total_installs().should.be.eql(3000)

@given('a user')
def step(context):
    context.user = User("Ivan")

@when('he rates an app')
def step(context):
    context.user.rate(context.app, 3)
    
@then('the user should have the app rating in his ratings')
def step(context):
    context.user.ratings.should.have.length_of(1)
    rated_apps = context.user.rated_apps()
    rated_apps[0].name.should.be.eql("100 Bucks")

@when('I enter the app market ratings')
def impl(context):
    context.app.add_market_rating(5.0)
    context.app.add_market_rating(1.0)

@then('I should see the average rating')
def impl(context):
    context.app.average_market_rating().should.be.eql(3.0)

@then('I should see the number of ratings')
def impl(context): context.app.market_rating_len().should.be.eql(2)

@given('{app_count} apps')
def impl(context, app_count):
    apps = []
    for i in range(int(app_count)):
        apps.append(App("App" + str(i), [Category("")], "" + str(i)))
    context.apps = apps

@when('2 users rate their apps')
def impl(context):
    users = []
    for i in range(2):
        users.append(User(str(i)))
    users[0].rate(context.apps[0], 3.0)
    users[0].rate(context.apps[1], 1.0)
    users[1].rate(context.apps[0], 2.5)
    users[1].rate(context.apps[1], 5.0)
    users[1].rate(context.apps[2], 4.0)
    users[1].rate(context.apps[3], 5.0)
    context.users = users

@when('I rate an app')
def impl(context):
    context.me = User("Me")
    context.me.rate(context.apps[0], 4.0)
    context.me.rate(context.apps[1], 4.0)
    context.me.rate(context.apps[2], 5.0)
    context.users.append(context.me)

@then('I should receive recommendations about new apps to install')
def impl(context):
    recommender = Recommender()
    recommendations = recommender.get_recommendations(context.users, context.me)
    recommendations[0][1].name.should.be.eql("App3")

@given('an user')
def impl(context):
    context.user = User.objects.first()

@when('he requests new apps to install')
def impl(context):
    request_json_data = context.web_app.get("/api/v1/recommend/" + str(context.user.id)).json
    context.apps = request_json_data

@then('he should receive list of recommended apps')
def impl(context):
    len(context.apps).should.eql(5)

@given('I am an administrator')
def impl(context):
    pass

@when('I create an user')
def impl(context):
    response = context.web_app.post_json('/api/v1/users', dict(username="Stamat"))
    context.user = response.json

@then('I should read it')
def impl(context):
    context.user['name'].should.eql("Stamat")

@then('delete it')
def impl(context):
    user_id = list(context.user['_id'].values())[0]
    context.web_app.delete_json('/api/v1/users', dict(user_id=user_id))

@given('existing user')
def impl(context):
    context.user_id = "519a546feece1115b047fb51"

@when('he wants to rate an app')
def impl(context):
    context.app_id = "519bacf9eece11769919ad89"

@then('he should send his rating')
def impl(context):
    context.web_app.post_json('/api/v1/apps/rate', dict(user_id=context.user_id, app_id=context.app_id, rating=4))
