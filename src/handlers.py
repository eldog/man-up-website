import os
import utils
import urllib
import datetime

from google.appengine.api import users
from google.appengine.api.mail import send_mail
from google.appengine.ext.webapp import RequestHandler, template

from models import Award, Badge, Member, NewsArticle, Meeting, Team, Talk

from manupcalendar import ManUpCalendar

get_path = utils.path_getter(__file__)

template.register_template_library('templatetags.customtags')

class BaseHandler(RequestHandler):

    login_required = False
    
    title = None
    
    def render_template(self, template_name, template_dict=None):
        next_meeting = Meeting.get_next_meeting()
        if next_meeting:
            tag_line = '%s: %s, %s' % (next_meeting.name, next_meeting.start_date, next_meeting.location)
        else:
            tag_line = 'Evening Hack: 14/4/2011 5pm LF15'
    
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
            other = member.gql('WHERE handle = :1', handle).get()
            
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
        post =  self.request.POST
        if post['kind'] == 'badge':
            badge = Badge(name=post['name'], description=post['description'], 
                      category=post['category'], image=post['image'],
                      value=int(post['value']))
            badge.save()
        elif post['kind'] == 'article':
            article = NewsArticle(title=post['title'], author=post['author'],
                             body=post['body'], date=datetime.date.today())
            article.save()
        elif post['kind'] == 'award':
            badge = Badge.get_by_id(int(post['badge']))
            for h in post.getall('members'):
                member = Member.get_by_id(int(h))
                a = Award(member=member,
                          badge=badge,
                          date=datetime.date.today(),
                          proof=post['proof'])
                a.save()
                member.score_cache = member.score + badge.value
                member.save()
        elif post['kind'] == 'talk':
            talk = Talk(title=post['title'],
                        description=post['description'],
                        member=Member.get_by_id(int(post['member'])),
                        meeting=Meeting.get_by_id(int(post['meeting'])))
            if post['video']:
                talk.video = post['video']
            talk.put()
        self.get()
            
    def get(self):
        self.render_template('admin', {'badges': Badge.all(),
                                       'members': Member.all(),
                                       'meetings': Meeting.all()})
        

class BadgeHandler(BaseHandler):

    def get(self, id):
        badge = Badge.get_by_id(id) #urllib.unquote(id))
        self.render_template('badge', {'badge': badge})


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
            self.render_template('badge_application', {'message': 'Application submitted. It will be reviewed as soon as possible.'})
        
    def get(self):
        selected_badge = self.request.GET.getall('badge')
        if selected_badge:
            selected_badge = selected_badge[0]
        else:
            selected_badge = None
        
        badges = Badge.gql('ORDER BY name')
        self.render_template('badge_application', {'badges': badges, 'selected_badge': selected_badge})
    

class BadgesHandler(BaseHandler):

    title = 'Badges'

    def get(self):
        order = self.request.GET.get('order', 'value')
        if order == 'receivers':
            b = list(Badge.all())
            b.sort(key=lambda i:i.awards.count())
        else:
            b = Badge.gql('ORDER BY ' + order)
        self.render_template('badges', {'badges': b})


class CalendarHandler(BaseHandler):

    def get(self):
        self.render_template('calendar')


class ContactHandler(BaseHandler):

    def get(self):
        self.render_template('contact')


class FAQHandler(BaseHandler):

    def get(self):
        self.render_template('faq')
        

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
        

class MeetingHandler(BaseHandler):

    def get(self):
        calendar = ManUpCalendar()
        feed = calendar.get_feed()
        for entry in feed.entry:
            for a_when in entry.when:
                date_string = a_when.start_raw[:19]
                date = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
                for where in entry.where:
                    meeting = Meeting(name=entry.title.text, start_date=date, location=where.value)
                    meeting.put()


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
            
        self.render_template('members', {'members': ranked_members})

        
class MemberHandler(BaseHandler):

    def get(self, handle):
        query = Member.gql('WHERE handle = :1', urllib.unquote(handle))
        member = iter(query).next() if query.count() else None
        self.render_template('member', {'member': member})


class MessagesHandler(BaseHandler):

    def get(self, message_index=None):
        message_path = 'static/messages/%s.html' % message_index
        self.response.out.write(open(message_path).read())


class NewsHandler(BaseHandler):

    def get(self):
        self.render_template('news')
        

class NewsLetterHandler(BaseHandler):

    _post_fields = frozenset(('start_date', 'end_date'))

    def post(self):
        post =  self.request.POST
        if 'start_date' in post.keys() and 'end_date' in post.keys():
            current_user = users.get_current_user()
            # Validate our dates
            start_date = post['start_date']
            end_date = post['end_date']
            email = 'email' in post.keys()
            try:
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
                datetime.datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                errors_dict = { 'date_error' : 'Invalid dates' }
                self.render_template('newsletter', {'errors' : errors_dict})
                return
            event_feed = self.get_feed(post['start_date'], post['end_date'])
            if email and current_user and current_user.email():
                self.email_newsletter(event_feed, target=current_user.email())
            self.display_results(event_feed)
        else:
            errors_dict = { 'date_error' : 'please enter start and end dates' }
            self.get(temp_dict={'errors' : errors_dict})
                   
    def get(self, temp_dict=None):
        user = users.get_current_user()
        email = None
        if user:
            email = user or user.email()
        if not temp_dict:
            temp_dict = {'email' : email}
        else:
            temp_dict['email'] = email
        if temp_dict:
            self.render_template('newsletter', temp_dict)
        
    def email_newsletter(self, template_dict, 
                         target='lloyd.w.henning@gmail.com, petersutton2009@gmail.com'):
        email_html_template_path = get_path(
            os.path.join('templates', 'newsletter_email.html'))
        email_body_template_path = get_path(
            os.path.join('templates', 'newsletter_email_plain.txt'))
        email_html = template.render(email_html_template_path, {'event_feed' : template_dict})
        email_body = template.render(email_body_template_path, {'event_feed' : template_dict})
        send_mail(
                sender='lloyd.w.henning@gmail.com',
                to=target,
                subject='Newsletter',
                body=email_body,
                html=email_html)
    
    def display_results(self, event_feed): 
        self.get(temp_dict={'event_feed' : event_feed})
    
    def get_feed(self, start, end):
        calendar = ManUpCalendar()
        return calendar.get_feed(start_date=start, end_date=end)
        

class NewsLetterTaskHandler(NewsLetterHandler):

    login_required = True

    def get(self):
        now = datetime.datetime.now()
        this_time_next_week = now + datetime.timedelta(weeks=1)
        self.email_newsletter(self.get_feed(now.strftime('%Y-%m-%d'), 
                              this_time_next_week.strftime('%Y-%m-%d')))


class TalksHandler(BaseHandler):

    def get(self):
        self.render_template('talks', {'talks' : Talk.all()})
        

class TeamsHandler(BaseHandler):

    def get(self):
        self.render_template('teams', {'teams' : list(Team.all())})

        
class TeamSubmissionHandler(BaseHandler):

    login_required = True
    
    def get(self):
        self.render_template('team_submission')
    
    def post(self):
        post = self.request.POST
        
        team = Team(name=post['team_name'])
        team.save()
        
        self.response.out.write("submitted")
