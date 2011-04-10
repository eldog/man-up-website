#!/usr/bin/python
import datetime

import gdata.calendar.client
import gdata.calendar.data

def get_date(dt):
	return datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.000Z').strftime(
		'%a, %d %B, %H:%M') 

def PrintCalendar(calendar_client, calendar_uri, start_date='2011-01-01', end_date='2011-07-01'):
	query = gdata.calendar.client.CalendarEventQuery()
	query.start_min = start_date
	query.start_max = end_date
	feed = calendar_client.GetCalendarsFeed(calendar_uri, desired_class=gdata.calendar.data.CalendarEventFeed, q=query)
	for entry in feed.entry:
		print entry.title.text
		for a_when in entry.when:
			print '\tStart time: %s' % get_date(a_when.start)
			print '\tEnd time:   %s' % get_date(a_when.end)
		print '\t%s' % entry.where[0].value
		print '\t%s' % entry.content.text
		

cID = 'eju99itjidm08o1csed11gchhs@group.calendar.google.com'

client = gdata.calendar.client.CalendarClient()
client.ClientLogin('manchester.up@gmail.com', 'gqHtZ50k', 'eldog')

uri = client.GetCalendarEventFeedUri(cID)

PrintCalendar(client, uri)

