import sys

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers import AccountHandler, AdminHandler, BadgeHandler, \
    BadgesHandler, BadgeApplicationHandler, CalendarHandler, ContactHandler, \
    FAQHandler, FileNotFoundHandler, HackathonHandler, LoginHandler, \
    ManualHandler, MasterclassHandler, MemberHandler, MembersHandler, \
    MessagesHandler, NewsHandler, TalksHandler

from migration.hacker_migration import HackerMigrator

application = WSGIApplication(
    (('/'                           , NewsHandler),
     ('/account'                    , AccountHandler),
     ('/admin'                      , AdminHandler),
     ('/admin/hacker_migration'     , HackerMigrator),
     ('/badges'                     , BadgesHandler),
     ('/badges/([^/]+)'             , BadgeHandler),
     ('/badge_application'          , BadgeApplicationHandler),
     ('/calendar'                   , CalendarHandler),
     ('/contact'                    , ContactHandler),
     ('/faq'                        , FAQHandler),
     ('/hack-a-thon'                , HackathonHandler),
     ('/login'                      , LoginHandler),
     ('/manual'                     , ManualHandler),
     ('/masterclass'                , MasterclassHandler),
     ('/members'                    , MembersHandler),
     ('/members/([^/]+)'            , MemberHandler),
     ('/messages/([^/]+)'           , MessagesHandler),
     ('/talks'                      , TalksHandler),
     ('/(.+)'                       , FileNotFoundHandler)),
    debug=True)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    run_wsgi_app(application)
    return 0

if __name__ == '__main__':
    exit(main())
