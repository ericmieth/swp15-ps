import unittest
#from config import basedir
from app import app, db

class Test_app(unittest.TestCase):
	
	#method called to prepare test fixture, contains required items or state
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./db/ps.sqlite'
		self.app = app.test_client
		db.create_all()
	
	#method called immediately after the test method, restore initial state
	def tearDown(self):
		db.session.remove()
		db.drop_all()
	
#	def test_home(self):
#		self.test_app = app.test_client()
#		response = self.test_app#.get('/', '/index.html')
#		self.assertEquals(response.status_code, 200)

	def test_semester_choice(self):
		"""test"""
		self.test_app = app.test_client()
		response = self.test_app.post('/semester_choice')
		self.assertEquals(response.status_code, '200')


if __name__ == '__main__':
	unittest.main()
