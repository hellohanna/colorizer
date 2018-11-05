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
    email = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.LargeBinary(), nullable=True)
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


class Dataset(db.Model):
    """User's datasets"""

    CREATED = 'CREATED'
    UPLOADED = 'UPLOADED'
    TRAINING_REQUESTED = 'TRAINING_REQUESTED'
    TRAINING_STARTED = 'TRAINING_STARTED'
    TRAINING_COMPLETED = 'TRAINING_COMPLETED'

    __tablename__ = "datasets"
    dataset_id = db.Column(db.Integer,
                            autoincrement=True,
                            primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    name = db.Column(db.String(100), nullable=True)
    dataset_filename = db.Column(db.String(255), nullable=True)
    model_filename = db.Column(db.String(255), nullable=True)
    process_bar = db.Column(db.Integer, nullable=True)
    state = db.Column(db.String(30), nullable=False, default=CREATED)
    user = db.relationship('User')


def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
    User.query.delete()
    Photo.query.delete()

    # Add user and photo
    user = User(email='hanna@gmail.com', password=b'$2b$12$AtliYTeZH.Pfj.Drlph6FO6Fyh0ps9rL0V.p5DZDMel8MrrcvtHXO')
    db.session.add(user)
    db.session.commit()



def connect_to_db(app, database_uri="postgresql:///testdb"):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will
    # leave you in a state of being able to work with the database
    # directly.

    from server import app
    connect_to_db(app)
    db.create_all()
    print('Done')
