from google.appengine.api import users
from google.appengine.ext import db

class Hacker(db.Model):
    user_id = db.StringProperty(required=True)
    email = db.StringProperty(default='')
    handle = db.StringProperty(required=True)
    real_name = db.StringProperty(default='')
    score_cache = db.IntegerProperty(default=-1)
    
    @property
    def score(self):
        if self.score_cache == -1:
            self.score_cache = sum(award.badge.value for award in self.awards)
            self.save()
        return self.score_cache
    
    @classmethod
    def get_current_hacker(cls):
        user = users.get_current_user()
        if not user:
            return
        user_id = user.user_id()
        hacker = cls.gql('WHERE user_id = :1', user_id).get()
        if not hacker:
            hacker = Hacker(user_id=user_id, handle=user_id)
            hacker.put()
        return hacker
        

class Badge(db.Model):
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    category = db.CategoryProperty(required=True)
    image = db.StringProperty(required=True)
    value = db.IntegerProperty(required=True)


class Award(db.Model):
    hacker = db.ReferenceProperty(Hacker, collection_name='awards')
    badge = db.ReferenceProperty(Badge, collection_name='awards')
    date = db.DateProperty(required=True)
    proof = db.StringProperty(default='')


class NewsArticle(db.Model):
    title = db.TextProperty(required=True)
    author = db.StringProperty(required=True)    
    date = db.DateProperty(required=True)
    body = db.TextProperty(required=True)