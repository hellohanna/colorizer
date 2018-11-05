import io
from unittest import TestCase
from server import app
from model import db, connect_to_db, User, Photo, example_data
import server
import bcrypt
import base64


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

        user = User(email='ivan@gmail.com', password=b'123')
        db.session.add(user)
        db.session.commit()

        created_user = User.query.filter(User.email=='ivan@gmail.com').one()


    def test_login(self):
        """Test login """

        result = self.client.post('/signin',
                                 data={'email': "hanna@gmail.com", 'password': '123'},
                                 follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Upload photo", result.data)
    

    def test_signup(self):
        """Test sign up a new user"""

        result = self.client.post(
            '/signup',
            data={'email': "lola@gmail.com", 'password': '123'},
        )

        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.headers['Location'], BASE_URL + '/library')
        user = User.query.filter(User.email == "lola@gmail.com").one()
        self.assertEqual(user.password, bcrypt.hashpw(b'123', user.password))


    def test_signup_unique(self):
        result1 = self.client.post(
            '/signup',
            data={'email': "lola@gmail.com", 'password': '123'},
        )
        result2 = self.client.post(
            '/signup',
            data={'email': "lola@gmail.com", 'password': '456'},
        )
        self.assertEqual(result2.status_code, 302)
        self.assertEqual(result2.headers['Location'], BASE_URL + '/')
        result3 = self.client.get('/')
        self.assertIn(b'email already exists', result3.data)


    def test_upload_image(self):
        """Test uploading new bw picture from library page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'

        data = dict(
            file=(io.BytesIO(b'test image'), "test.jpg"),
        )
        res = self.client.post(
            '/upload', content_type='multipart/form-data', data=data,
        )
        self.assertEqual(res.status_code, 302)
        self.assertIn(BASE_URL + '/processing/', res.headers['Location'])


    def test_colorize_image(self):
        """Colorizing bw image"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = '1'

        b64 = (
            b'/9j/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOC'
            b'wkJDRENDg8QEBEQCgwSExIQEw8QEBD/yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQ'
            b'EAAD8A0s8g/9k='
        )

        data = dict(
            file=(io.BytesIO(base64.b64decode(b64)), "test.jpg"),
        )
        res1 = self.client.post(
            '/upload', content_type='multipart/form-data', data=data,
        )

        res2 = self.client.post(
            '/process/1', content_type='application/json', data=b'{}',
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(
            res2.data,
            b'http://hb-colorizer.s3.amazonaws.com/1_test_fake_B.png'
        )


if __name__ == '__main__':
    import unittest
    
    unittest.main()

