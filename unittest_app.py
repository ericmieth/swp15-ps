#!/usr/bin/python3
import unittest
from flask import Flask, request, url_for, redirect
from app import app, db

class Test_app(unittest.TestCase):
	
	#method called to prepare test fixture, contains required items or state
	def setUp(self):
		app.config['SECRET_KEY'] = 'SECRET_KEY'
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./db/ps.sqlite'
		self.test_app = app.test_client()
		db.create_all()
	
	#method called immediately after the test method, restores initial state
	def tearDown(self):
		db.session.remove()

	#test for home()
	def test_home(self):
		response = self.test_app.get('/')
		self.assertEqual(response.status_code, 200)
	
	#test for home() that the correct html template is rendered
	def test_template_home(self):
		response = self.test_app.get('/', content_type='html/text')
		self.assertTrue(b'Willkommen' in response.data)

	#test for study_choice()
	def test_study_choice(self):
		response = self.test_app.get('/study_choice')
		self.assertEqual(response.status_code, 200)
	
	#test for study_choice() that the correct html template is rendered
	def test_template_study_choice(self):
		response = self.test_app.get('/study_choice', content_type='html/text')
		self.assertTrue(b'Studiengangwahl' in response.data, response.data)

	#test for semester_choice()
	def test_semester_choice(self):
		response = self.test_app.post('/semester_choice', follow_redirects=True)
		self.assertEqual(response.status_code, 200)

	#test for module_choices()
	def test_module_choices(self):
		response2 = self.test_app.get('/module_choices')
		self.assertEqual(response2.status_code, 200)

	#test for module_choices() that the correct html template is rendered
	def test_template_module_choices(self):
		response = self.test_app.get('/module_choices', content_type='html/text')
		self.assertTrue(b'Modulwahl' in response.data)

	#test for lv_choice()
	def test_lv_choice(self):
		response1 = self.test_app.post('/lv_choice')
		self.assertEqual(response1.status_code, 200)
		response2 = self.test_app.get('/lv_choice')
		self.assertEqual(response2.status_code, 200)

	#test for lv_choice() that the correct html template is rendered
	def test_template_lv_choice(self):
		response = self.test_app.get('/lv_choice', content_type='html/text')
		self.assertTrue(b'LV-Wahl' in response.data)

	#test for lv_cust()
	def test_Lv_cust(self):
		response1 = self.test_app.post('/lv_cust')
		self.assertEqual(response1.status_code, 200)
		response2 = self.test_app.get('/lv_cust')
		self.assertEqual(response2.status_code, 200)

	#test for lv_cust() that the correct html template is rendered
	def test_template_lv_cust(self):
		response = self.test_app.get('/lv_cust', content_type='html/text')
		self.assertTrue(b'LV-Anpassung' in response.data)

	#test for calendar_preview(uid)
	def test_calendar_preview(self):
		response = self.test_app.get('/calendar_preview/{uid}')
		self.assertEqual(response.status_code, 200)

	#test for calendar_preview() that the correct html template is rendered
	def test_template_calendar_preview(self):
		response = self.test_app.get('/calendar_preview/{uid}',\
									 content_type='html/text')
		self.assertTrue(b'Kalendervorschau' in response.data)

	#test for calendar_download()
	def test_calendar_download(self):
		response = self.test_app.get('/calendar_download')
		self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
	unittest.main()