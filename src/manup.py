from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers import AccountPage, AdminPage, BadgePage, BadgesPage, \
    BadgeApplicationHandler, CalendarPage, ContactPage, FAQPage, ManualPage, MemberPage, MembersPage, \
    MessagesHandler, NewsPage, ProjectsPage, LoginHandler

application = WSGIApplication(
    [('/'               , NewsPage),
     ('/account'        , AccountPage),
     ('/admin'          , AdminPage),
     ('/badges'         , BadgesPage),
     ('/badges/([^/]+)' , BadgePage),
     ('/badge_application' , BadgeApplicationHandler),
     ('/calendar'       , CalendarPage),
     ('/contact'        , ContactPage),
     ('/faq'            , FAQPage),
     ('/login'          , LoginHandler),
     ('/manual'         , ManualPage),
     ('/members'        , MembersPage),
     ('/members/([^/]+)', MemberPage),
     ('/messages/(\d+)' , MessagesHandler),
     ('/projects'       , ProjectsPage)],
    debug=True)

def main(argv=None):
    run_wsgi_app(application)
    return 0
    
if __name__ == '__main__':
    exit(main())
