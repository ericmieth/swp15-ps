#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set noet ci pi sts=0 sw=4 ts=4:
import sparql_requests
import datetime


def semester(date: "date to convert"=None) -> \
"converted date for semester-specification":
	"""Converts the given (or current if none is given)
		date to a semester-specific format:

		"xyy"
	where
		- x is the first letter of the semester season
			(i.e. "w" for winter, "s" for summer)
		- y is the last to numbers of the year

	Examples:
		>>> semester(datetime.date(2015, 12, 5))
		'w15'
		>>> semester(datetime.date(2016, 1, 13))
		'w15'
		>>> semester(datetime.date(2015, 4, 19))
		's15'
		>>> semester(datetime.date(2015, 1, 5))
		'w14'
		>>> semester(datetime.date(2016, 6, 11))
		's16'
		>>> semester(datetime.date(2014, 11, 6))
		'w14'
	"""
	if date is None:
		given_date = datetime.date.today()
	else:
		given_date = date

	#list for the return of the semester query
	semester_list = []
	semester_list = sparql_requests.date_finder()
	#parameter for the for-loop
	x=0
	#default since the first 'if' has to be a success in case we only have one
	#summer or winter semester
	ws_begin = datetime.date(given_date.year-5, 1, 1)
	ss_begin = datetime.date(given_date.year-5, 1, 1)
	ws_end = datetime.date(given_date.year-5, 1, 1)
	ss_end = datetime.date(given_date.year-5, 1, 1)

	#determining of the last summer- and wintersemester
	for s_type in semester_list:
		if semester_list[x]["type"] == 'W':
			if ws_begin < semester_list[x]["begin"]:
				ws_begin = semester_list[x]["begin"]
				ws_end = semester_list[x]["end"]
		elif semester_list[x]["type"] == 'S':
			if ss_begin < semester_list[x]["begin"]:
				ss_begin = semester_list[x]["begin"]
				ss_end = semester_list[x]["end"]
		x += 1

	#Differentiation between the latest semester
	if ss_end < ws_end:
		if given_date < ss_begin:					#last winter semester
			if given_date.month < 6:				#next year date
				return "w"+str(given_date.year-1)[-2:]
			elif given_date.month >= 6:				#current year date
				return "w"+str(given_date.year)[-2:]
		elif given_date <= ss_end:  				#current summer semester
			return "s"+str(given_date.year)[-2:]
		elif given_date <= ws_end:  				#current winter semester
			if given_date.month < 6:				#next year date
				return "w"+str(given_date.year-1)[-2:]
			elif given_date.month >= 6:				#current year date
				return "w"+str(given_date.year)[-2:]
		elif ws_end < given_date:
			return "s"+str(given_date.year)[-2:]
	#Reverse situation from above. Effectively swapping the semesters
	elif ws_end < ss_end:
		if given_date < ws_begin:					#last summer semester
			return "s"+str(given_date.year)[-2:]
		elif given_date <= ws_end:					#current winter semester
			if given_date.month < 6:				#next year date
				return "w"+str(given_date.year-1)[-2:]
			elif given_date.month >= 6:				#current year date
				return "w"+str(given_date.year)[-2:]
		elif given_date <= ss_end:  				#current summer semester
			return "s"+str(given_date.year)[-2:]
		elif ss_end < given_date:					#next winter semester
			if given_date.month < 6:				#next year date
				return "w"+str(given_date.year-1)[-2:]
			elif given_date.month >= 6:				#current year date
				return "w"+str(given_date.year)[-2:]


def first_day(day) -> "date of the first weekday in current semester":
	"""Determines the the firt date of a weekday in this semester

	Examples:
		>>> first_day("di")
		datetime.date(2015, 4, 7)
		>>> first_day("mi")
		datetime.date(2015, 4, 8)
	"""
	first_day = semester_begin()

	# dictionary to get weekdaynumbers
	weekdaynumber = {"mo": 0, "di": 1, "mi": 2, "do": 3, "fr": 4, "sa": 5, "so": 6}

	# increments the day of the date until the weekdays match
	while(first_day.weekday() != weekdaynumber[day]):
		if(first_day.day == 30):
			first_day = datetime.date(first_day.year, first_day.month + 1, 1)
			continue
		first_day = datetime.date(first_day.year, first_day.month, first_day.day+1)

	return first_day


def semester_begin(date: "date to convert"=None) -> \
"begin of the specified winter- or summersemester":
	"""Determines the starting date for the calendar from a given date.

	Examples:
		>>> semester_begin(datetime.date(2015, 3, 1))
		datetime.date(2015, 4, 7)
		>>> semester_begin(datetime.date(2015, 11, 11))
		datetime.date(2015, 10, 12)
	"""
	if date is None:
		given_date = datetime.date.today()
	else:
		given_date = date

	#list for the return of the semester query
	semester_list = []
	semester_list = sparql_requests.date_finder()
	#parameter for the for-loop
	x=0
	#default since the first 'if' has to be a success in case we only have one
	#summer or winter semester
	ws_begin = datetime.date(given_date.year-5, 1, 1)
	ss_begin = datetime.date(given_date.year-5, 1, 1)
	ws_end = datetime.date(given_date.year-5, 1, 1)
	ss_end = datetime.date(given_date.year-5, 1, 1)

	#determining of the last summer- and wintersemester
	for s_type in semester_list:
		if semester_list[x]["type"] == 'W':
			if ws_begin < semester_list[x]["begin"]:
				ws_begin = semester_list[x]["begin"]
				ws_end = semester_list[x]["end"]
		elif semester_list[x]["type"] == 'S':
			if ss_begin < semester_list[x]["begin"]:
				ss_begin = semester_list[x]["begin"]
				ss_end = semester_list[x]["end"]
		x += 1

	#Checking which semester is the last one, then returning the begin of the
	#semester in question.
	if ss_end < ws_end:
		if given_date <= ss_end:  					#current summer semester
			return ss_begin
		elif given_date <= ws_end:  				#current winter semester
			return ws_begin#TODO abfangen eines Datums, was nicht im Bereich ist? Sinnvoll ja/nein?
	elif ws_end < ss_end:
		if given_date <= ws_end:  					#current winter semester
			return ws_begin
		elif given_date <= ss_end:  				#current summer semester
			return ss_begin


def lecture_end(date: "date to convert"=None) -> \
"end of the specified semester":
	"""Determines the ending date for the calendar from a given date.

	Examples:
		>>> lecture_end(datetime.date(2016, 1, 1))
		datetime.date(2016, 2, 6)
		>>> lecture_end(datetime.date(2015, 3, 1))
		datetime.date(2015, 7, 18)
		>>> lecture_end(datetime.date(2015, 11, 11))
		datetime.date(2016, 2, 6)
	"""
	if date is None:
		given_date = datetime.date.today()
	else:
		given_date = date

	#list for the return of the semester query
	semester_list = []
	semester_list = sparql_requests.date_finder()
	#parameter for the for-loop
	x=0
	#default since the first 'if' has to be a success in case we only have one
	#summer or winter semester
	ws_begin = datetime.date(given_date.year-5, 1, 1)
	ss_begin = datetime.date(given_date.year-5, 1, 1)
	ws_end = datetime.date(given_date.year-5, 1, 1)
	ss_end = datetime.date(given_date.year-5, 1, 1)

	#determining of the last summer- and wintersemester
	for s_type in semester_list:
		if semester_list[x]["type"] == 'W':
			if ws_begin < semester_list[x]["begin"]:
				ws_begin = semester_list[x]["begin"]
				ws_end = semester_list[x]["end"]
		elif semester_list[x]["type"] == 'S':
			if ss_begin < semester_list[x]["begin"]:
				ss_begin = semester_list[x]["begin"]
				ss_end = semester_list[x]["end"]
		x += 1

	#Checking which semester is the last one, then returning the end of the
	#semester in question.
	if ss_end < ws_end:
		if given_date <= ss_end:  					#current summer semester
			return ss_end
		elif given_date <= ws_end:  				#current winter semester
			return ws_end
	elif ws_end < ss_end:#TODO siehe TODO oben, gleiches hier
		if given_date <= ws_end:  					#current winter semester
			return ws_end
		elif given_date <= ss_end:  				#current summer semester
			return ss_end


def semester_numbers(semester_numbers:\
					 "list of numbers which represent semesters",\
					 season: "\"s\" for summer-, \"w\" for winter-semester"\
					 =None) -> "relevant semester-numbers":
	"""Determines the available semester for this season.
	Assumptions: summer has even number,
	every course of study begins in semester 1.
	
	Examples:
		>>> semester_numbers([1,2,3,4,5,6], "s")
		[2, 4, 6]
		>>> semester_numbers([1,2,3,4], "w")
		[1, 3]
	"""
	if season is not ("w" or "s"):
		season = semester()[:1]
	if season == "w":
		return semester_numbers[::2]
	else:
		return semester_numbers[1::2]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
