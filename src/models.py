from google.appengine.api import users
from google.appengine.ext import db

class Member(db.Model):

    user_id = db.StringProperty(required=True)
    email = db.StringProperty(default='')
    handle = db.StringProperty(required=True)
    bio = db.TextProperty(default='')
    real_name = db.StringProperty(default='')

    @property
    def score(self):
        return sum(award.badge.value for award in self.awards)
    
    @classmethod
    def get_current_member(cls):
        user = users.get_current_user()
        if not user:
            return
        user_id = user.user_id()
        member = cls.gql('WHERE user_id = :1', user_id).get()
        if not member:
            member = cls(user_id=user_id, handle=user_id)
            member.put()
        return member

# Ironic hack, so that we can do data migration. Will need to be deleted in future
# Release    
class Hacker(Member):
    pass    

class Badge(db.Model):
    name = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    category = db.CategoryProperty(required=True)
    image = db.StringProperty(required=True)
    value = db.IntegerProperty(required=True)


class Award(db.Model):

    member = db.ReferenceProperty(Member, collection_name='awards')
    badge = db.ReferenceProperty(Badge, collection_name='awards')
    date = db.DateProperty(required=True)
    proof = db.StringProperty(default='')


class NewsArticle(db.Model):

    title = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    date = db.DateProperty(required=True)
    body = db.TextProperty(required=True)


class Talk(db.Model):

    title = db.StringProperty()
    member = db.ReferenceProperty(Member, required=True, collection_name='talks')
    date = db.DateProperty(required=True)
    video = db.LinkProperty(required=True)
    description = db.TextProperty()
