import sys

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers import AccountHandler, AdminHandler, BadgeHandler, \
    BadgesHandler, BadgeApplicationHandler, CalendarHandler, ContactHandler, \
    FAQHandler, HackathonHandler, LoginHandler, ManualHandler, \
    MasterclassHandler, MemberHandler, MembersHandler, \
    MessagesHandler, NewsHandler, NewsLetterHandler, NewsLetterTaskHandler, \
    TalksHandler, TeamsHandler, TeamSubmissionHandler

application = WSGIApplication(
    (('/'                  , NewsHandler),
     ('/account'           , AccountHandler),
     ('/admin'             , AdminHandler),
     ('/badges'            , BadgesHandler),
     ('/badges/([^/]+)'    , BadgeHandler),
     ('/badge_application' , BadgeApplicationHandler),
     ('/calendar'          , CalendarHandler),
     ('/contact'           , ContactHandler),
     ('/faq'               , FAQHandler),
     ('/hack-a-thon'       , HackathonHandler),
     ('/login'             , LoginHandler),
     ('/manual'            , ManualHandler),
     ('/masterclass'       , MasterclassHandler),
     ('/members'           , MembersHandler),
     ('/members/([^/]+)'   , MemberHandler),
     ('/messages/(\d+)'    , MessagesHandler),
     ('/newsletter'        , NewsLetterHandler),
     ('/task/newsletter'   , NewsLetterTaskHandler),
     ('/talk'              , TalksHandler),
     ('/teams'             , TeamsHandler),
     ('/team_submission'   , TeamSubmissionHandler)),
    debug=True)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    run_wsgi_app(application)
    return 0
    
if __name__ == '__main__':
    exit(main())
