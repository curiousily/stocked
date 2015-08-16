from math import *

class Recommender:

    DEFAULT_RATING=4.0

    def pearson_similarity(self, user1, user2):
        similar_apps = []
        for app in user1.installed_apps:
            if app in user2.installed_apps:
                similar_apps.append(app)
        app_len = float(len(similar_apps))
        if app_len == 0: return -1.0

        u1_rate_sum = float(sum(user1.rating_of(app, default_rating=Recommender.DEFAULT_RATING) for app in similar_apps))
        u2_rate_sum = float(sum(user2.rating_of(app, default_rating=Recommender.DEFAULT_RATING) for app in similar_apps))

        u1_sqr_sum = float(sum(pow(user1.rating_of(app,
            default_rating=Recommender.DEFAULT_RATING), 2) for app in similar_apps))
        u2_sqr_sum = float(sum(pow(user2.rating_of(app,
            default_rating=Recommender.DEFAULT_RATING), 2) for app in similar_apps))

        sum_prod = float(sum(user1.rating_of(app,
            default_rating=Recommender.DEFAULT_RATING) * user2.rating_of(app,
                default_rating=Recommender.DEFAULT_RATING) for app in similar_apps))

        num=(app_len*sum_prod)-(1.0*u1_rate_sum*u2_rate_sum)
        den1=sqrt((app_len*u1_sqr_sum)-float(pow(u1_rate_sum,2)))
        den2=sqrt((app_len*u2_sqr_sum)-float(pow(u2_rate_sum,2)))
        den=1.0*den1*den2

        if den == 0: return 0

        result = num / den
        return result

    def get_recommendations(self, users, person):
        totals = {}
        similarity_sums = {}

        for other in users:
            if other == person: continue
            similarity = self.pearson_similarity(person, other)

            if similarity <= 0: continue

            for app in other.installed_apps:

                if app not in person.installed_apps:

                    totals.setdefault(app, 0)
                    totals[app] += other.rating_of(app,
                            default_rating=Recommender.DEFAULT_RATING) * similarity

                    similarity_sums.setdefault(app, 0)
                    similarity_sums[app] += similarity

        rankings = [(total/similarity_sums[app], app) for app, total in totals.items()]
        rankings.sort()
        rankings.reverse()
        return rankings
