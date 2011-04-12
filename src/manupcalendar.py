#!/usr/bin/python
import datetime

import gdata.calendar.client
import gdata.calendar.data

class ManUpCalendar():

    client = gdata.calendar.client.CalendarClient()

    def __init__(
        self, cID='eju99itjidm08o1csed11gchhs@group.calendar.google.com'):
        self.client.ClientLogin('manchester.up@gmail.com', 'gqHtZ50k', 'eldog')
        self.uri = self.client.GetCalendarEventFeedUri(cID)

    def get_date(self, dt):
        return datetime.datetime.strptime(
            dt, '%Y-%m-%dT%H:%M:%S.000Z').strftime(
                '%a, %d %B, %H:%M') 

    def get_feed(self, start_date='2011-01-01', end_date='2011-07-01'):
        query = gdata.calendar.client.CalendarEventQuery()
        query.start_min = start_date
        query.start_max = end_date
        feed = self.client.GetCalendarsFeed(
            self.uri,
            desired_class=gdata.calendar.data.CalendarEventFeed,
            q=query)
        # edit the dates so they look right...
        for entry in feed.entry:
            for when in entry.when:
                # remember their old forms for adding them to the db if necessary
                when.start_raw = when.start
                when.end_raw = when.end
                # make them pretty
                when.start = self.get_date(when.start)
                when.end = self.get_date(when.end)
        return feed
        
    def print_calendar(self, start_date='2011-01-01', end_date='2011-07-01'):
        feed = get_feed()
        for entry in feed.entry:
            print entry.title.text
            for a_when in entry.when:
                print '\tStart time: %s' % self.get_date(a_when.start)
                print '\tEnd time:   %s' % self.get_date(a_when.end)
            print '\t%s' % entry.where[0].value
            print '\t%s' % entry.content.text

if __name__ == '__main__':
    calendar = ManUpCalendar()
    calendar.print_calendar()

