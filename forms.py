#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set noet ci pi sts=0 sw=4 ts=4:
from flask.ext.wtf import Form
from wtforms import SelectField, SelectMultipleField, SubmitField, FormField, \
DateField, RadioField, FieldList
from wtforms import widgets


class course_form(Form):
	"""Creates the dropdown-list for the choice of the courses of study."""
	course = SelectField('Studiengang')


class multi_checkbox_field(SelectMultipleField):
	"""Creates multicheckboxes for the possibilities of the courses of study."""
	widget = widgets.ListWidget(prefix_label=False)
	option_widget = widgets.CheckboxInput()


class modules_form(Form):
	"""Creates the multiple possibilities to choose modules and the buttons to
		confirm the choice and proceed."""
	all_modules = multi_checkbox_field('')
	study_course_modules = multi_checkbox_field('')
	choosen_modules = multi_checkbox_field('')
	choice = SubmitField("Wählen")
	cont = SubmitField("weiter")


class module_form(Form):
	"""Creates the list with dates for the chosen modules."""
	enddate = DateField("Datum der letzten Vorlesung")
	course = RadioField("Übung")


class lv_form(Form):
	"""Creates the multicheckboxes for the possibilities to choose the modules
		and the buttons to confirm the choice and proceed."""
	cont = SubmitField("weiter")
