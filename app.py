#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set noet ci pi sts=0 sw=4 ts=4:

# self-implemented modules
import sparql_requests
import time_conversion
import ical
import forms
import datetime

# library for configuration
from config import c

# Flask-imports
from flask import Flask, render_template, request, escape, session, url_for,\
					redirect, Response, g, flash

# libaries needed for database
import hashlib
import random
from flask.ext.sqlalchemy import SQLAlchemy
import pickle

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % c["user_db"]["path"]
app.secret_key = c["webserver"]["secret_key"]
db = SQLAlchemy(app)


class Student(db.Model):
	"""flask sqlalchemy database for app.py"""
	id = db.Column(db.String(40), primary_key=True)
	# links course of study to database
	study_course = db.Column(db.String(80))
	# links semester to database
	semester = db.Column(db.SmallInteger)
	# links modules to database
	modules = db.Column(db.PickleType(protocol=pickle.HIGHEST_PROTOCOL))
	# links last download to database
	last_download = db.Column(db.DateTime)
	addresses = db.relationship('Choice', backref='student', lazy='select')

	def __init__(self, id):
		self.id = id


class Lv(db.Model):
	uri = db.Column(db.String(80), primary_key=True)
	# last change made in OD.fmi fpr this lv
	last_changed = db.Column(db.DateTime)
	day = db.Column(db.String(10))
	# starting time
	begin = db.Column(db.String(5))
	# end time
	end = db.Column(db.String(5))
	lecturer = db.Column(db.String(40))
	room = db.Column(db.String(20))
	addresses = db.relationship('Choice', backref='lv', lazy='select')

	def __init__(self, uri):
		self.uri = uri


class Choice(db.Model):
	id = db.Column(db.String(40), db.ForeignKey('student.id'), primary_key=True)
	uri = db.Column(db.String(80), db.ForeignKey('lv.uri'), primary_key=True)
	enddate = db.Column(db.DateTime)

	def __init__(self, id, uri):
		self.id = id
		self.uri = uri

db.create_all()


@app.before_request
def usermanagement():
	"""Management of the ids of the current sessions"""
	def new_student():
		"""Creates an id for the user, where all relevant information
			are saved
		"""
		g.student = Student(hashlib.sha1(str(random.random())
											.encode('utf-8')).hexdigest())
		g.student.endtimes = dict()
		g.student.modules = []
		# adds g.student to current database transaction
		db.session.add(g.student)
		session["id"] = g.student.id

	# Session restore
	if "id" in session:
		# gets g.student from database via session id
		g.student = Student.query.get(session["id"])
		if g.student is None:
			new_student()

	elif request.endpoint != 'calendar_preview':
		new_student()
	else:
		# TODO sessionrestore?!
		pass


@app.after_request
def save_db(response_class) -> "response_class":
	"""Saves changes made in this request to database (commits transaction)"""
	db.session.commit()
	return response_class


@app.route("/")
@app.route("/index.html")
def home() -> "returns initial webpage":
	"""Initial webpage, will later show a instruction."""
	return render_template("home.html")


@app.route("/study_choice")
def study_choice() \
	-> "returns selection for course of studies\
		as webpage (study_choice.html)":
	"""First step.
	Creates a webpage, which shows a drop-down menu with all courses of study.
	"""
	# sets the sparql-requests for course of studies
	study_course = sparql_requests.get_course_of_studies()
	# sets form (DropDownList) for courses
	form = forms.course_form()
	# sets the choice
	form.course.choices = study_course
	# flask looks for required template in templates folder and renders it
	return render_template("study_choice.html", form=form)


@app.route("/semester_choice", methods=['POST'])
def semester_choice() \
	-> "returns semester selection\
		as webpage (semester_choice.html)":
	"""Second step. Creates a webpage, which shows all semester."""
	form = forms.course_form()
	study_course = sparql_requests.get_course_of_studies()
	form.course.choices = study_course
	# will check if it is a POST request and if it is valid
	if form.validate_on_submit():
		g.student.study_course = request.form["course"]
	else:
		return redirect(url_for("study_choice"))
	semester = sparql_requests.semester_finder(g.student.study_course)
	semester = time_conversion.semester_numbers(semester)
	return render_template("semester_choice.html", semester=semester)


@app.route('/add_default_modules', methods=['POST'])
def add_default_modules() -> "redirects to next step":
	"""Selects all default modules
		for the choosen semester and course of studies.
	"""
	g.student.semester = request.form["semester"]
	modules = sparql_requests.module_finder(
					g.student.study_course,
					g.student.semester)
	# saves the data the sparql-request got in the current database
	g.student.modules = list(set(modules))
	return redirect(url_for("module_choices"))


@app.route("/module_choices", methods=['POST', 'GET'])
def module_choices() -> "returns module selection\
as webpage (module_choices.html)":
	"""Creates a webpage
		where the user can select modules from three different lists.
	"""
	study_course_modules = sparql_requests.module_finder(g.student.study_course)
	all_modules = sparql_requests.module_finder()

	modules_name_dict = {uri: name for uri, name in all_modules}

	form = forms.modules_form()
	form.choosen_modules.choices = g.student.modules
	form.all_modules.choices = list(set(all_modules).difference
									(g.student.modules).difference
									(study_course_modules))
	form.study_course_modules.choices = list(set(study_course_modules)
											.difference(g.student.modules))

	# will check if it is a POST request and if it is valid
	if form.validate_on_submit():
		choosen_modules_set = {(uri, modules_name_dict[uri])
								for uri in form.all_modules.data}
		choosen_modules_set.update({(uri, modules_name_dict[uri])
								for uri in form.choosen_modules.data})
		choosen_modules_set.update({(uri, modules_name_dict[uri])
								for uri in form.study_course_modules.data})
		g.student.modules = list(choosen_modules_set)

		if form.cont.data:
			return redirect(url_for('lv_choice'))

		# update choices, they may have changed
		form.choosen_modules.choices = g.student.modules
		form.all_modules.choices = list(set(all_modules)
			.difference(g.student.modules).difference(study_course_modules))
		form.study_course_modules.choices = list(set(study_course_modules)
											.difference(g.student.modules))

	form.choosen_modules.data = [uri for uri, _ in g.student.modules]

	return render_template("module_choices.html", form=form)


@app.route("/lv_choice", methods=['POST', 'GET'])
def lv_choice() -> "returns all events to the selected modules (lvwahl.html)":
	"""Fourth step. Creates a webpage,
		which shows all events to the selected modules."""
	course_set = {lv.uri for lv in
				Lv.query.join(Choice).filter(Choice.id == g.student.id)}
	# set sparql-request to get all needed events
	lvs = sparql_requests.get_lv_for_modules(
							[uri for uri, _ in g.student.modules])

	modules_name_dict = {uri: name for uri, name in g.student.modules}

	class lv_form(forms.lv_form):
		pass
	for modul, extra in lvs.items():
		course_tupel = list()
		course_uris = list()
		for uri in extra:
			title, day, begin, end, lecturer, place = extra[uri]
			course_tupel.append((uri, "%s %s %s - %s bei %s" % (title,
					day, begin, end, lecturer)))
			course_uris.append(uri)

		defaults = list(filter(lambda uri: uri in course_set, course_uris))

		class New_form(forms.Form):
			label = modules_name_dict[modul]
			course = forms.multi_checkbox_field(
					"Übung",
					choices=course_tupel,
					default=defaults)
		setattr(lv_form, modules_name_dict[modul], forms.FormField(New_form))
	form = lv_form()

	def lv_equal(db_lv, uri, day, begin, end, lecturer, room):
		if db_lv is None or db_lv.day != day or db_lv.begin != begin \
				or db_lv.end != end or db_lv.lecturer != lecturer \
				or db_lv.room != room:
			return False
		else:
			return True

	def update_db_lv(db_lv, uri, day, begin, end, lecturer, room):
		if db_lv is None:
			db_lv = Lv(uri)
		db_lv.day, db_lv.begin, db_lv.end, db_lv.lecturer, db_lv.room = \
										day, begin, end, lecturer, room
		db_lv.last_changed = datetime.datetime.now()
		db.session.add(db_lv)

	# if something changes in the backend update our copy
	#TODO select performance
	for modul_uri in lvs:
		for uri in lvs[modul_uri]:
			title, day, begin, end, lecturer, room = lvs[modul_uri][uri]
			db_lv = Lv.query.get(uri)
			if not lv_equal(db_lv, uri, day, begin, end, lecturer, room):
				update_db_lv(db_lv, uri, day, begin, end, lecturer, room)

	# will check if it is a POST request and if it is valid
	if form.validate_on_submit():
		Choice.query.filter(Choice.student == g.student).delete()
		course_set = set()
		for modul in lvs:
			subform = getattr(form, modules_name_dict[modul])
			course_set.update(subform.course.data)
		for course in course_set:
			db.session.add(Choice(session["id"], course))
		if form.cont.data:
			return redirect(url_for('lv_cust'))
	return render_template("lv_choice.html", form=form)


@app.route("/lv_cust", methods=['POST', 'GET'])
def lv_cust() -> "returns all lectures with semester enddates":
	"""Creates a webpage,
		where the user can change the enddate for the selected modules"""
	lvs = [lv.uri for lv in
				Lv.query.join(Choice).filter(Choice.id == g.student.id)]
	# set the sparql-request to get lectures of choosen modules
	lvinfos = sparql_requests.get_lv_info(lvs)

	class lv_form(forms.lv_form):
		pass
	for uri in lvinfos:
		title, start, end, day, location = lvinfos[uri]
		lv_tupel = (uri,
			"%s %s %s - %s in %s" % (title, day, start, end, location))
		endtime = Choice.query.get((g.student.id, uri)).enddate
		if endtime is None:
			endtime = time_conversion.lecture_end()

		class New_form(forms.Form):
			label = title
			enddate = forms.DateField("Datum der letzten Veranstaltung",
									default=endtime)
		setattr(lv_form, title, forms.FormField(New_form))
	form = lv_form()

	endtimes = dict()
	# will check if it is a POST request and if it is valid
	if form.validate_on_submit():
		for uri in lvinfos:
			subform = getattr(form, lvinfos[uri][0])
			enddate = subform.enddate.data
			c = Choice.query.get((g.student.id, uri))
			c.enddate = enddate
			db.session.add(c)
		if form.cont.data:
			# redirects the user to another endpoint with session-id
			return redirect(url_for('calendar_preview', uid=session['id']))
	return render_template("lv_cust.html", form=form)


@app.route("/calendar_preview/<uid>")
def calendar_preview(uid=None) -> "preview of the created calendar":
	"""Creates a Webpage
		with all selected modules and events in a calendar preview.
	"""
	# writes uid into session if lost
	if uid is not None:
		session["id"] = uid
		usermanagement()

	if g.student.last_download is not None:
		updated_courses = Lv.query.join(Choice)\
							.filter(Choice.id == g.student.id)\
							.filter(Lv.last_changed > g.student.last_download)
		for updated_course in updated_courses:
			flash("Kurs %s wurde am %s geändert" % (updated_course.uri,
								updated_course.last_changed))

	courses = [choice.lv.uri for choice in g.student.addresses]
	weekdays, lines = ical.mk_fortnight(sparql_requests.get_lv_info(courses))
	return render_template("calendar_preview.html", weekdays=weekdays, lines=lines)


@app.route("/calendar_download")
def calendar_download() ->"returns ps.ics as download":
	"""Downloads the created calendar as ical file"""

	lvs = {choice.uri: choice.enddate for choice in g.student.addresses}
	cal = ical.mk_ical(sparql_requests.get_lv_info(lvs.keys()), lvs)
	response = Response(cal.to_ical(),
						mimetype="text/calendar",
						headers={"Content-Disposition":
							"attachment; filename=stundenplan.ics"})
	g.student.last_download = datetime.datetime.now()
	return response


if __name__ == "__main__":
	app.run(
		host=c["webserver"]["host"],
		port=c["webserver"]["port"],
		debug=c["debug"])
