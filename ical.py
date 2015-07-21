#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set noet ci pi sts=0 sw=4 ts=4:
from icalendar import Calendar, Event, vRecur
import datetime
import time_conversion

weekdays_dict = {
	"montags": "MO",
	"dienstags": "TU",
	"mittwochs": "WE",
	"donnerstags": "TH",
	"freitags": "FR",
	"samstags": "SA",
	"sonntags": "SU"
}
"""Dict from german weekday name to the english shorthand used by odfmi"""

biweekly = dict()
for day in weekdays_dict:
	biweekly[day] = (weekdays_dict[day], "")				# beide?
	biweekly[day + " (ZL)"] = (weekdays_dict[day], "")		# ????
	biweekly[day + " (A-Woche)"] = (weekdays_dict[day], "A")
	biweekly[day + " (B-Woche)"] = (weekdays_dict[day], "B")


def mk_ical(lvinfos: "dict of lvinfos uri:(title,start,end,day,location)",
			endtimes: "dict of enddates uri:date"
			) -> "ical callendar":
	"""
	Creates an ical callendar from lvinfos and endtimes.
	"""
	cal = Calendar()
	cal.add('prodid', '-//swt-ps//python-icalendar//DE')
	cal.add('version', '2.0')
	for uri in lvinfos:
		title, start, end, day, location = lvinfos[uri]
		event = Event()
		event.add('uid', uri)
		event.add('location', location)
		start_day = time_conversion.first_day(lvinfos[uri][3][:2])
		shour, sminute = start.split(':')
		ehour, eminute = end.split(':')
		sttime = datetime.datetime(start_day.year, start_day.month,
					start_day.day, hour=int(shour), minute=int(sminute))
		endtime = datetime.datetime(start_day.year, start_day.month,
					start_day.day, hour=int(ehour), minute=int(eminute))
		event.add('dtstamp', datetime.datetime.today())
		event.add('summary', title)
		recur = vRecur(byday=biweekly[day][0], freq='weekly',
						until=endtimes[uri])
		if biweekly[day][1] == "A":
			if start_day.isocalendar()[1] % 2 == 0:
				sttime = sttime + datetime.timedelta(weeks=1)
				endzeit = endzeit + datetime.timedelta(weeks=1)
			recur['interval'] = 2
		elif biweekly[day][1] == "B":
			if start_day.isocalendar()[1] % 2 == 1:
				sttime = sttime + datetime.timedelta(weeks=1)
				endtime = endtime + datetime.timedelta(weeks=1)
			recur['interval'] = 2
		event.add('dtstart', sttime)
		event.add('dtend', endtime)
		event.add('rrule', recur)
		cal.add_component(event)
	return cal

weekdayorder = {
	('MO', 'A'): 0,
	('TU', 'A'): 1,
	('WE', 'A'): 2,
	('TH', 'A'): 3,
	('FR', 'A'): 4,
	('SA', 'A'): 5,
	('SU', 'A'): 6,
	('MO', 'B'): 7,
	('TU', 'B'): 8,
	('WE', 'B'): 9,
	('TH', 'B'): 10,
	('FR', 'B'): 11,
	('SA', 'B'): 12,
	('SU', 'B'): 13}
"""weekday shorthands in their natural order (day, week):index"""


def mk_fortnight(lvinfos: "dict of lvinfos uri:(title,begin,end,weekday,room)"
		) -> "\
	returns a tuple containing two things, the names of the weekdays in their\
	natural order and a twodimensional array, with each row represeting one\
	timeslot. the first collumn is the name of the timeslot.\
	":
	"""
	Generates a biweekly table from lvinfos
	"""
	# slots are timeslots, some lvs start at :00 some start at :15,
	# both are equivalent for our needs
	slots = ["7:30", "9:15", "11:15", "13:15", "15:15",
				"17:15", "19:15", "21:15"]
	slots2 = [slot.replace(":15", ":00") for slot in slots]

	two_weeks = dict()
	# set up empty weekdayname -> slots dict
	for day in biweekly:
		# only if we have A or B, don't create one for ""
		# which is both weeks
		if biweekly[day][1] != "":
			two_weeks[biweekly[day]] = [set() for slot in slots]
	# put the data we got into the empty structure we just generated
	for uri in lvinfos:
		title, begin, end, weekday, room = lvinfos[uri]
		# if it does not start at :15 it starts at :00
		if begin in slots:
			index = slots.index(begin)
		elif begin in slots2:
			index = slots2.index(begin)
		else:
			break
			# throw some kinda error, strange beginning time
			# can't put that into the table
		# "" means this lv happens in both weeks
		if biweekly[weekday][1] == "":	  # expand to both weeks
			two_weeks[(biweekly[weekday][0], "A")][index]\
					.add((title, begin, end, room))
			two_weeks[(biweekly[weekday][0], "B")][index]\
					.add((title, begin, end, room))
		else:
			two_weeks[biweekly[weekday]][index].add((title, begin, end, room))
	# sort by week day (see weekdayorder) and return
	sorted_weekdays = sorted(
							two_weeks.items(),
							key=lambda i: weekdayorder[i[0]])
	veranstaltungen = [veranstaltungen for
						tag_name, veranstaltungen in sorted_weekdays]
	rotated = list()
	for i in range(len(slots)):
		rotated.append([tag[i] for tag in veranstaltungen])
	sorted_weekdaynames = ["%s %s" % label for label, _ in sorted_weekdays]
	return sorted_weekdaynames, list(zip(slots, rotated))
