import datetime
import os
import utils
import urllib

from google.appengine.api import users
from google.appengine.api.mail import send_mail
from google.appengine.ext.webapp import RequestHandler, template
from google.appengine.ext.db import GqlQuery

import utils
from models import Award, Badge, Hacker, NewsArticle, Talk

get_path = utils.path_getter(__file__)

class BaseHandler(RequestHandler):

    login_required = False
    title = None

    def render_template(self, template_name, template_dict=None):
        tag_line = 'Next meeting coming soon'

        if template_dict is None:
            template_dict = {}
        
        user = Member.get_current_member()
        
        if user:
            if self.login_required:
                redirect_target = '/'
            else:
                redirect_target = self.request.path
            url_creator = users.create_logout_url
        else:
            redirect_target = '/login?url=%s' % self.request.path
            url_creator = users.create_login_url

        defaults = {
            'user': user,
            'is_admin': users.is_current_user_admin(),
            'log_url': url_creator(redirect_target),
            'tag_line': tag_line,
            'title': self.title
        }

        for key in defaults:
            if key not in template_dict:
                template_dict[key] = defaults[key]

        template_path = get_path(
            os.path.join('templates', '%s.html' % template_name)
        )
        self.response.out.write(template.render(template_path, template_dict))


class AccountHandler(BaseHandler):

    login_required = True

    title = 'Account'

    valid_letters = (
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )
    
    banned_names = {
        u'neo': "Fat chance are you Neo. If you are, I'm not gonna get my hopes up",
    }
    
    def post(self):
        if len(self.request.POST) == 4 and 'handle' in self.request.POST \
                and 'real_name' in self.request.POST \
                and 'email' in self.request.POST \
                and 'bio' in self.request.POST:

            handle = self.request.POST.getall('handle')[0]
            template_dict = {}
            member = Member.get_current_member()
            other = Member.gql('WHERE handle = :1', handle).get()
            
            if (not handle or len(handle) > 12 or
                any(l not in self.valid_letters for l in handle)):
                template_dict['error'] = 'Pick something sensible, you moron.'
            
            elif other and other.user_id != member.user_id:
                template_dict['error'] = 'Sorry, already taken.'

            elif handle.lower() in self.banned_names:
                template_dict['error'] = self.banned_names[handle]

            else:
                real_name = self.request.POST.getall('real_name')[0]
                if real_name:
                    member.real_name = real_name
                email = self.request.POST.getall('email')[0]
                if email:
                    member.email = email
                bio = self.request.POST.getall('bio')[0]
                if bio:
                    member.bio = bio
                member.handle = handle
                member.save()
                template_dict['error'] = 'Profile updated'
            self.render_template('account', template_dict)
            
    def get(self):
        self.render_template('account')


class AdminHandler(BaseHandler):

    login_required = True

    def post(self):
        post = self.request.POST
        if post['kind'] == 'badge':
            badge = Badge(
                name=post['name'],
                description=post['description'],
                category=post['category'], 
                image=post['image'],
                value=int(post['value'])
            )
            badge.save()
        elif post['kind'] == 'article':
            date = datetime.datetime.strptime(post['date'], '%Y-%m-%d').date()
            article = NewsArticle(
                title=post['title'], 
                author=post['author'],
                body=post['body'], 
                date=date
            )
            article.save()
        elif post['kind'] == 'award':
            badge = Badge.get_by_id(int(post['badge']))
            for member in post.getall('members'):#remove getall()
                member = Member.get_by_id(int(member))
                award = Award(
                    member=member,
                    badge=badge,
                    date=datetime.date.today(),
                    proof=post['proof']
                )
                award.save()
                member.score_cache = member.score + badge.value
                member.save()
        elif post['kind'] == 'talk':
            talk = Talk(
                title=post['title'],
                date=datetime.datetime.strptime(post['date'], '%Y-%m-%d').date(),
                description=post['description'],
                member=Member.get_by_id(int(post['member'])),
                meeting=Meeting.get_by_id(int(post['meeting']))
                video=post['video']
            )
            talk.put()
        self.get()

    def get(self):
        self.render_template('admin', {
            'badges': Badge.all(),
            'members': Member.all(),
            'meetings': Meeting.all()
        })
        

class BadgeHandler(BaseHandler):

    def get(self, id):
        self.render_template('badge', {
            'badge': Badge.get_by_id(id) #urllib.unquote(id)) XXX
        })


class BadgeApplicationHandler(BaseHandler):

    login_required = True

    def post(self):
        post = self.request.POST
        if len(post) == 2 and 'badge' in post and 'proof' in post:
            body = 'Member: %s\nBadge: %s\nProof:\n%s' % (
                Member.get_current_member().handle, post['badge'], 
                post['proof'])
            send_mail(
                sender='petersutton2009@gmail.com',
                to='petersutton2009@gmail.com',
                subject='Badge application',
                body=body)
            self.render_template('badge_application', {
                'message': 'Application submitted. \
                            It will be reviewed as soon as possible.'
            })

    def get(self):
        selected_badge = self.request.GET.getall('badge')
        if selected_badge:
            selected_badge = selected_badge[0]
        else:
            selected_badge = None
        badges = Badge.gql('ORDER BY name')
        self.render_template('badge_application', {
            'badges': badges,
            'selected_badge': selected_badge
        })


class BadgesHandler(BaseHandler):

    title = 'Badges'

    def get(self):
        order = self.request.GET.get('order', 'value')
        if order == 'receivers':
            badges = list(Badge.all())
            badges.sort(key=lambda i:i.awards.count())
        else:
            badges = Badge.gql('ORDER BY ' + order)
        self.render_template('badges', {
            'badges': badges
        })


class CalendarHandler(BaseHandler):

    def get(self):
        self.render_template('calendar')


class ContactHandler(BaseHandler):

    def get(self):
        self.render_template('contact')


class FAQHandler(BaseHandler):

    def get(self):
        self.render_template('faq')
        

class FileNotFoundHandler(BaseHandler):
    def get(self, handler_name=''):
        self.render_template('404', {
            'url' : handler_name
        })

class HackathonHandler(BaseHandler):

    def get(self):
        self.render_template('hack-a-thon')


class ManualHandler(BaseHandler):

    def get(self):
        self.render_template('manual')


# This handler is a hack to force people to select handles.
class LoginHandler(BaseHandler):

    def get(self):
        if 'url' in self.request.GET:
            member = Member.get_current_member()
            if member.handle.isdigit() and len(member.handle) == 21:
                self.redirect('/account')
            else:
                self.redirect(self.request.GET.getall('url')[0])
        else:
            self.redirect('/')
            
class MasterclassHandler(BaseHandler):

    def get(self):
        self.render_template('masterclass')


class MembersHandler(BaseHandler):
    
    def get(self):
        members = list(Member.all())
        if members:
            members.sort(key=lambda member:(member.score, member.handle))
            rank = 0
            ranked_members = [(rank, members[-1])]
            for i in range(len(members)-2, 0, -1):
                if members[i + 1].score_cache != members[i].score_cache:
                    rank += 1
                ranked_members.append((rank, members[i]))
        else:
            ranked_members = []
            
        self.render_template('members', {
            'members': ranked_members
        })


class MemberHandler(BaseHandler):

    def get(self, handle):
        query = Member.gql('WHERE handle = :1', urllib.unquote(handle))
        member = iter(query).next() if query.count() else None
        self.render_template('member', {
            'member': member
        })


class MessagesHandler(BaseHandler):

    def get(self, message_index=None):
        if message_index == None:
            self.render_template('404', {'url' : 'message number ' + message_index})
        else:
            message_path = 'static/messages/%s.html' % message_index
            cur_file = None
            try:
                cur_file = open(message_path)
                self.response.out.write(cur_file.read())
            except IOError:
                self.render_template('404', {'url' : 'message number ' + message_index})
            finally:
                if cur_file:
                    cur_file.close()


class NewsHandler(BaseHandler):

    def get(self):
        news_list = GqlQuery('SELECT * FROM NewsArticle ORDER BY date DESC');
        self.render_template('news', {
            'news_list': news_list
        })


class TalksHandler(BaseHandler):

    def get(self):
        self.render_template('talks', {
            'talks' : Talk.all()
        })
