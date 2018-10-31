from unittest import TestCase
from server import app
from model import db, connect_to_db, User, Photo, example_data
import server


BASE_URL = "http://localhost"

class StaticTests(TestCase):
    """Flask static tests"""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'

        connect_to_db(app, "postgresql:///test")
        #app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        db.create_all()

    def tearDown(self):
        """Stuff to do after each test."""
        db.session.commit()
        db.drop_all()
        db.session.close()

    def test_homepage(self):
        """Test to see Start button on the homepage"""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<button>Start</button>', result.data)

    def test_library(self):
        """Test lbrary page"""

        result = self.client.get("/library")
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Upload photo", result.data)

    def test_map(self):
        """Test page with google map"""

        result = self.client.get('/map')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<iframe', result.data)

    def test_logout(self):
        """Test logout """

        result = self.client.get('/logout')
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.headers['Location'], BASE_URL + '/')

    def test_empty_upload(self):
        """Test empty file upload"""

        result = self.client.post('/upload')
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.headers['Location'], BASE_URL + '/library')


class DatabaseTests(TestCase):
    """Database flask tests"""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()
        # Connect to test database
        
        connect_to_db(app, "postgresql:///test")
        db.create_all()
        example_data()


    def tearDown(self):
        """Do at end of every test."""

        db.session.commit()
        db.drop_all()
        db.session.close()


    def test_create_user(self):
        """Add new user in DB"""

        user = User(email='hanna@gmail', password=b'123')
        db.session.add(user)
        db.session.commit()

        created_user = User.query.filter(User.email=='hanna@gmail').one()


    def test_login(self):
        """Test login """

        result = self.client.post('/signin',
                                 data={'email': "anylike@gmail", 'password': '123'},
                                 follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Upload photo", result.data)


    

    def test_signup(self):
        """Test sign up a new user"""


    def test_upload_image(self):
        """Test uploading new bw picture from library page"""


    def test_processing_image(self):
        """Colorizing bw image"""


  

if __name__ == '__main__':
    import unittest
    
    unittest.main()

