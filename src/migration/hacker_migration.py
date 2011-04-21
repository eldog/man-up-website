'''

Handler that migrates any old Hacker entities to Member entities

'''
import urllib

from handlers import BaseHandler
from models import Award, Hacker, Member, NewsArticle, Talk

class HackerMigrator(BaseHandler):
    # Request handler for the URL /update_datastore
    def get(self):
        handle = self.request.get('handle', None)
        if handle is None:
            # First request, just get the first handle out of the datastore.
            hacker = Hacker.gql('ORDER BY handle DESC').get()
            if not hacker:
                # No hackers in database
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write("No Hackers in database")
                return
            handle = hacker.handle
    
        query = Hacker.gql('WHERE handle <= :1 ORDER BY handle DESC', handle)
        hackers = query.fetch(limit=2)
        current_hacker = hackers[0]
        if len(hackers) == 2:
            next_handle = hackers[1].handle
            next_url = '/admin/hacker_migration?handle=%s' % urllib.quote(next_handle)
        else:
            next_handle = 'FINISHED'
            next_url = '/'  # Finished processing, go back to main page.
            
            
        awards_updated = 0
        talks_updated = 0
        updated_hacker = False
        # Add a new member if this Hacker has not been migrated
        if not Member.gql('WHERE handle = :1', current_hacker.handle).get():
            new_member = Member(user_id=current_hacker.user_id,
                                email=current_hacker.email,
                                handle=current_hacker.handle,
                                bio=current_hacker.bio,
                                real_name=current_hacker.real_name)
            new_member.put()
            
            # Find any award or talk entities that reference the old hacker 
            # and remap them
            awards = Award.gql('WHERE hacker = :1', current_hacker)
            for award in awards:
                award.member = new_member
                if hasattr(award, 'hacker'):
                    del award.hacker
                award.put()
                awards_updated += 1
            talks = Talk.gql('WHERE member = :1', current_hacker)
            for talk in talks:
                talk.member = new_member
                talk.put()
                talks_updated += 1
                    
            updated_hacker = True
    
        # Delete the Hacker
        current_hacker.delete()
    
        context = {
            'current_handle': handle,
            'updated_hacker': updated_hacker,
            'awards_updated': awards_updated,
            'talks_updated': talks_updated,
            'next_handle': next_handle,
            'next_url': next_url,
        }
        
        self.render_template('hacker_migration', context)