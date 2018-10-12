from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting
# this through the Flask-SQLAlchemy helper library. On this, we can
# find the `session` object, where we do most of our interactions
# (like committing, etc.)

db = SQLAlchemy()

# Model definitions

class User(db.Model):
    """User of colorizing website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    name = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} email={self.email}>"

    photo = db.relationship('Photo')

class Photo(db.Model):
    """Photos of users"""

    __tablename__ = "photos" 

    photo_id = db.Column(db.Integer,
                         autoincrement=True,
                         primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    original_photo = db.Column(db.String(300), nullable=True)
    processed_photo = db.Column(db.String(300), nullable=True)

    user = db.relationship('User')


def example_data():
    """Create some example data."""

  
    jane = User(name='Jane', email='jdoe@gmail.com', password='1234')
    alice = User(name='Alice', email='aperson@hotmail.com', password='2134')
    bob = User(name='Bob', email='bpersonne@yahoo.com', password='qwerty')
    
    photos = [
    Photo(user_id=jane.user_id,original_photo="https://www.digitalphotomentor.com/photography/2016/12/creating-good-black-white-28.jpg",processed_photo="https://www.digitalphotomentor.com/photography/2016/12/creating-good-black-white-28.jpg"),
    Photo(user_id=alice.user_id,original_photo="https://www.digitalphotomentor.com/photography/2016/12/creating-good-black-white-28.jpg",processed_photo="https://www.digitalphotomentor.com/photography/2016/12/creating-good-black-white-28.jpg"),
    Photo(user_id=bob.user_id,original_photo="https://www.digitalphotomentor.com/photography/2016/12/creating-good-black-white-28.jpg",processed_photo="https://www.digitalphotomentor.com/photography/2016/12/creating-good-black-white-28.jpg")
    ]

    db.session.add_all(photos)
    db.session.commit()

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///testdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will
    # leave you in a state of being able to work with the database
    # directly.

    from server import app
    connect_to_db(app)
    
    print("Connected to DB.")
