from mongoengine import *

connect('tsunapper')

class MarketRating(EmbeddedDocument):

    rating = FloatField()
    rate_count = IntField()

class DownloadCount(EmbeddedDocument):

    low_range = IntField()
    high_range = IntField()

class Category(Document):

    name = StringField()

class Publisher(Document):

    name = StringField()

class AppRating(EmbeddedDocument):
    user = ReferenceField('User')
    rating = FloatField()

class App(Document):

    name = StringField()
    package = StringField()
    publisher = ReferenceField(Publisher)
    icon_url = StringField()
    categories = ListField(ReferenceField(Category))
    url = StringField()
    crawled = BooleanField()
    market_rating = EmbeddedDocumentField(MarketRating)
    download_count = EmbeddedDocumentField(DownloadCount)
    images = ListField(StringField())
    description = StringField()
    ratings = ListField(EmbeddedDocumentField(AppRating), default=[])

    def rate(self, user, rating):
        self.ratings.append(AppRating(user=user, rating=rating))

    def __eq__(self, other):
        return self.package == other.package

    def __hash__(self):
        return hash(self.package)

class User(Document):
    first_name = StringField()
    last_name = StringField()
    email = StringField()
    provider = StringField()
    provider_id = StringField()
    friends = ListField(ReferenceField('self', reverse_delete_rule=NULLIFY))
    installed_apps = ListField(ReferenceField(App))
    recommended_apps = ListField(ReferenceField(App))

    def rating_of(self, app, default_rating=0.0):
        for rating in app.ratings:
            if rating.user.provider_id == self.provider_id:
                return rating.rating
        return default_rating

    def __eq__(self, other):
        return self.provider_id == other.provider_id

class AppCrawlList(Document):
    apps = ListField(StringField())
