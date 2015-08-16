import jsonpickle
from jsonpickle.handlers import BaseHandler

class UserHandler(BaseHandler):

    def flatten(self, obj, data):
        data['firstName'] = obj.first_name
        data['lastName'] = obj.last_name
        data['provider'] = obj.provider
        data['providerId'] = obj.provider_id
        data['email'] = obj.email

        return data

class AppListItemHandler(BaseHandler):

    def flatten(self, obj, data):

        data['name'] = obj.name
        data['publisher'] = obj.publisher.name
        data['url'] = obj.url
        data['appPackage'] = obj.package
        data['iconUrl'] = obj.icon_url

        return data


class AppDetailHandler(AppListItemHandler):

    def flatten(self, obj, data):
        super(AppDetailHandler, self).flatten(obj, data)
        data['description'] = obj.description
        data['marketRating'] = {}
        data['marketRating']['rating'] = obj.market_rating.rating
        data['marketRating']['rateCount'] = obj.market_rating.rate_count
        data['downloadCount'] = {}
        data['downloadCount']['lowRange'] = obj.download_count.low_range
        data['downloadCount']['highRange'] = obj.download_count.high_range
        data['images'] = obj.images
        return data
