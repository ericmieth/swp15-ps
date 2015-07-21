#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set noet ci pi sts=0 sw=4 ts=4:
from SPARQLWrapper import SPARQLWrapper, JSON
import time_conversion
import datetime

from config import c  # libary for configuration

wrapper = SPARQLWrapper(c["ODFMI"]["url"], returnFormat=JSON)


def get_course_of_studies() -> "list of all moduls of all courses of study":
	"""Finds all listed courses of studies (Bc. Inf., Dipl. Mathematik, ...)

	Returns list in form of [(uri, titel), (uri,titel), …,]
	"""
	wrapper.resetQuery()
	wrapper.setQuery("""
		SELECT ?studyCourse, ?studyCourseURI
		WHERE {
			?studyCourseURI rdf:type <http://od.fmi.uni-leipzig.de/model/Studiengang>.
			?studyCourseURI rdfs:label ?studyCourse.
		} ORDER BY ASC(?studyCourse)""")
	results = wrapper.query().convert()
	return [(result["studyCourseURI"]["value"], result["studyCourse"]["value"])
		for result in results["results"]["bindings"]]


def module_finder(
		study_course: "course of studies"=None,
		semester: "semester"=None
		) -> "list of all modules of a chosen course of study":
	"""Returns a list of modules.

	Returns either all listed modules in the database or,
	if a course of study or a semester is given, the recommended ones
	"""
	wrapper.resetQuery()
	query = """
	SELECT distinct ?modulLabel, ?modul
	WHERE {"""
	if study_course is not None:
		query += """
		?semesterStudyCourse od:toStudiengang <%s>.
		""" % study_course
	if semester is not None:
		query += """
		?semesterStudyCourse rdfs:label ?semesterStudyCourseLabel.
		FILTER REGEX(?semesterStudyCourseLabel, ".*%s")
		""" % semester
	if semester is not None or study_course is not None:
		query += """
		?modul od:toStudiengangSemester ?semesterStudyCourse.
		"""
	query += """
		?modul rdfs:label ?modulLabel.
		?unit od:relatedModule ?modul.
		?unit od:containsKurs ?kurs.
		?kurs od:containsLV ?LV.
		?LV rdf:type <http://od.fmi.uni-leipzig.de/model/LV>
		FILTER REGEX(?LV, ".*%s.*")
	} ORDER BY ASC(?modulLabel)""" % time_conversion.semester()

	wrapper.setQuery(query)
	results = wrapper.query().convert()
	return [(result["modul"]["value"], result["modulLabel"]["value"])
		for result in results["results"]["bindings"]]


def get_lv_for_modules(
		modules: "list of modules (URI)",
		optional: "set this to True to get get only optional units"=False,
		mandatory: "set this to True to get get only lectures"=False
		) -> "module:lv:(label, weekday, begin, end, by, location":
	"""finds information about the modules lvs"""

	from multiprocessing.pool import ThreadPool
	ret = {modul: dict() for modul in modules}
	ret = dict()
	querys = list()
	for modul in modules:
		query = """
		SELECT distinct ?LV, ?LVlabel, ?LVdayOfWeek, ?LVbeginsAt, ?LVendsAt, ?LVservedBy, ?LVlocation
		WHERE {
			?unit od:relatedModule <%s>.
			?unit od:containsKurs ?kurs.
			?kurs od:containsLV ?LV.
			?LV rdf:type <http://od.fmi.uni-leipzig.de/model/LV>
			FILTER REGEX(?LV, ".*%s.*")
			?LV rdfs:label ?LVlabel.
			?LV od:beginsAt ?LVbeginsAt.
			?LV od:endsAt ?LVendsAt.
			?LV od:servedBy ?LVservedBy.
			?LV od:dayOfWeek ?LVdayOfWeek.
			?LV rdf:type ?typ.
			?LV od:locatedAt ?LVlocationURI.
			?LVlocationURI rdfs:label ?LVlocation.
			FILTER(?typ != <http://od.fmi.uni-leipzig.de/model/LV>)
			""" % (modul, time_conversion.semester())
		if optional:
			query += """
			FILTER(?typ = <http://od.fmi.uni-leipzig.de/model/Praktikum> || ?typ = <http://od.fmi.uni-leipzig.de/model/Uebung> )"""
		if mandatory:
			query += """
			FILTER(?typ != <http://od.fmi.uni-leipzig.de/model/Praktikum> && ?typ != <http://od.fmi.uni-leipzig.de/model/Uebung> )"""
		query += """
			?typ rdfs:label ?typLabel.
		}"""
		querys.append(query)

	def execute_query(query):
		my_wrapper = SPARQLWrapper("http://od.fmi.uni-leipzig.de:8892/sparql", returnFormat=JSON)
		my_wrapper.resetQuery()
		my_wrapper.setQuery(query)
		results = my_wrapper.query().convert()
		ret = dict()
		for result in results["results"]["bindings"]:
			uri = result["LV"]["value"]
			by = get_trainer(result["LVservedBy"]["value"])
			if uri in ret:
				ret[uri][4] += " & " + by
			else:
				titel = result["LVlabel"]["value"]
				day = result["LVdayOfWeek"]["value"]
				begin = result["LVbeginsAt"]["value"]
				end = result["LVendsAt"]["value"]
				loc =result["LVlocation"]["value"]
				ret[uri] = [titel, day, begin, end, by, loc]
		return {uri: tuple(ret[uri]) for uri in ret}

	# increase 8 to moar for even moooar paralelz
	p = ThreadPool(8)
	modul_infos = p.map(execute_query, querys)
	return {module: modul_info for module, modul_info in zip(modules, modul_infos)}


def get_lv_info(lvs: "list of courses (URI)") \
	-> "list of information for given courses":
	"""Returns information about the given courses.

	These information contain like the course-name, appointed time, location.
	"""
	ret = {lv: dict() for lv in lvs}
	wrapper.resetQuery()
	if len(lvs) > 0:  # if list isn't empty
		query = """
		SELECT distinct ?LV, ?LVlabel, ?LVbeginsAt, ?LVendsAt, ?LVlocation, ?LVdayOfWeek
		WHERE {
			?LV rdfs:label ?LVlabel.
			?LV od:beginsAt ?LVbeginsAt.
			?LV od:endsAt ?LVendsAt.
			?LV od:locatedAt ?LVlocationURI.
			?LVlocationURI rdfs:label ?LVlocation.
			?LV od:dayOfWeek ?LVdayOfWeek.
			FILTER(?LV IN (%s))
		}""" % ", ".join(["<%s>" % uri for uri in lvs])
		wrapper.setQuery(query)
		results = wrapper.query().convert()
		ret = dict()
		for result in results["results"]["bindings"]:
			ret[result["LV"]["value"]] = (result["LVlabel"]["value"],
									result["LVbeginsAt"]["value"],
									result["LVendsAt"]["value"],
									result["LVdayOfWeek"]["value"],
									result["LVlocation"]["value"])
	return ret


def semester_finder(
		study_course: "course of studies"
		) -> "number of semester to a course of study":
	"""Returns all available semester to the given course of study"""
	wrapper.resetQuery()
	query = """
	SELECT ?semester
	WHERE {
	?semester od:toStudiengang <%s>.
	?semester rdf:type <http://od.fmi.uni-leipzig.de/model/StudiengangSemester>.
	?semester rdfs:label ?semesterLabel.
	} ORDER BY ASC(?semester)""" % study_course

	wrapper.setQuery(query)
	results = wrapper.query().convert()
	results = [(result["semester"]["value"]).split(study_course + ".")[-1]
		for result in results["results"]["bindings"]]
	try:
		results = sorted(results, key=int)
	except ValueError:
		results.sort()
	return results


def date_finder() -> "double-indexed dictionary, containing beginning and\
			ending of a all semesters in database":
	"""Extracts beginning and ending of a all semesters in database and returns them"""
	wrapper.resetQuery()
	query = """
	SELECT ?type ?begin ?end
	WHERE {
	?object od:hasSemesterType ?type.
	?object od:beginDate ?begin.
	?object od:endDate ?end.
	FILTER (!REGEX(?type, ".*P.*")).
	} """
	wrapper.setQuery(query)
	results = wrapper.query().convert()
	dates_list = []

	for result in results["results"]["bindings"]:
		date_begin = datetime.datetime.strptime(result["begin"]["value"], "%Y-%m-%d")
		date_begin = date_begin.date()

		date_end = datetime.datetime.strptime(result["end"]["value"], "%Y-%m-%d")
		date_end = date_end.date()

		dates_list.append({"type": result["type"]["value"],
						"begin": date_begin, "end": date_end})
	return dates_list


def get_trainer(trainerURI: "URI of trainer"
		) -> "name of a trainer if found, else N.N.":
	"""Extracts the trainer-name for a given URI and resturns it"""
	wrapper.resetQuery()
	query = """
	SELECT ?trainerName
	WHERE {
	<%s> foaf:name ?trainerName
	} """ % trainerURI
	wrapper.setQuery(query)
	results = wrapper.query().convert()
	if not results["results"]["bindings"]:
		print("No foaf:name found in URI <" + trainerURI + ">.")
		return "N.N."
	return results["results"]["bindings"][0]["trainerName"]["value"]
