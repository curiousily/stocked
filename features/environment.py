from behave import *
from stocked.models import App, Category
from webtest import TestApp
import webapp

def before_all(context):
    context.app = App("100 Bucks", [Category("Money")], "http://apps.com/100Bucks")
    context.web_app = TestApp(webapp.app)
