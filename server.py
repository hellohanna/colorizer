from jinja2 import StrictUndefined
import colorize
import shutil
import re
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from model import connect_to_db, db, User, Photo, Dataset

from PIL import Image
import bcrypt
import os
import s3

from werkzeug.utils import secure_filename




UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.add_template_global(s3.url_for, name='s3_url_for')
app.add_template_global(False, name='navbar_transparent')




# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raise an error if there is undefined variable in Jinja2.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/signin', methods=['POST'])
def signin():
    """Check if user exists. Redirect to the library"""

    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter(User.email==email).first()
    if not user:
        flash("No such user")
        return redirect("/")

    if user.password != bcrypt.hashpw(password.encode(), user.password):
        flash("Incorrect password")
        return redirect("/")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/library")


@app.route('/signup', methods= ['POST'])
def signup():
    """Add info about new user in a database. Log in a new user"""

    email = request.form.get('email')
    match_obj = re.search(r"(\w+)\@(\w+\.com)", email)
    if match_obj is None:
        flash("Incorrect email address")
        return redirect('/')
    password = request.form.get('password')
    name = request.form.get('name', '').strip()
    if not name:
        flash("Name can't be empty")
        return redirect('/')

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    try:
        new_user = User(email=email, password=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        flash('User with this email already exists')
        return redirect('/')

    # Add new user to the session
    new_user = User.query.filter(User.email==email).one()
    session['user_id'] = new_user.user_id

    flash("User {} added.".format(name))
    return redirect("/library")


@app.route("/library")
def user_detail():
    """Show user's library."""

    user_id = session.get("user_id")

    # Checking if the user is logged in a system
    if user_id:
        user = User.query.get(user_id)
        photos = Photo.query.filter(Photo.user_id==user_id).order_by(Photo.photo_id.desc()).all()
        return render_template("library.html", user=user, photos=photos)

    # If user is not logged in send him back to the homepage
    else:
        flash("You are not logged in.")
        return redirect('/')


def allowed_photo_filename(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']

@app.route('/upload', methods=['POST'])
def upload():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect('/library')
    file = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect('/library')
    if file and allowed_photo_filename(file.filename):
        new_photo = Photo(user_id=session['user_id'])
        db.session.add(new_photo)
        db.session.flush()

        filename = f'{new_photo.photo_id}_{secure_filename(file.filename)}'
        s3.upload(file, filename)

        new_photo.original_photo = filename
        db.session.commit()

        return redirect(f'/processing/{new_photo.photo_id}')


@app.route('/processing/<photo_id>')
def photo_processing(photo_id):
    """Photo processing page"""

    photo = Photo.query.filter(
        Photo.user_id == session['user_id'],
        Photo.photo_id == photo_id,
    ).first()

    if not photo:
        return redirect('/library')

    datasets = Dataset.query.filter(
        Dataset.state == Dataset.TRAINING_COMPLETED
    ).all()

    return render_template("processing.html", photo=photo, datasets=datasets)


@app.route('/process/<photo_id>', methods=['POST'])
def process_photo(photo_id):
    """Convert photo"""

    json = request.get_json()
    dataset_id = json.get('dataset_id', 0)

    if dataset_id == 0:
        model_name = 'portraits_pix2pix'
    else:
        dataset = Dataset.query.filter(
            Dataset.state == Dataset.TRAINING_COMPLETED,
            Dataset.dataset_id == dataset_id,
            Dataset.user_id == session['user_id'],
        ).one()
        model_name = dataset.model_filename

    photo = Photo.query.filter(
        Photo.user_id == session['user_id'],
        Photo.photo_id == photo_id,
    ).one()

    s3.get_image(photo.original_photo)
   
    processed_filename = colorize.process(
        UPLOAD_FOLDER, photo.original_photo, model_name
    )
    photo.processed_photo = processed_filename
    db.session.commit()
    
    file = open(os.path.join(app.config['UPLOAD_FOLDER'], processed_filename), 'rb')
    s3.upload(file, processed_filename, content_type='image/png')
    url=s3.url_for(processed_filename)
    return url


@app.route('/map')
def show_map():
    """Map page"""

    return render_template("map.html", google_api_key=os.environ.get('GOOGLE_API_KEY', ''))


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


@app.route('/training')
def training_page():
    """Show training set page"""

    datasets = Dataset.query.filter(Dataset.user_id == session['user_id']).all()
    return render_template("training.html", datasets=datasets)


def allowed_dataset_filename(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['zip']


@app.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    # check if the post request has the file part
    if 'file' not in request.files or not request.files['file'].filename:
        flash('No file specified')
        return redirect('/training')

    file = request.files['file']
    if not allowed_dataset_filename(file.filename):
        flash("Only .zip files are allowed")
        return redirect('/training')

    name = request.form['name']
    if not name:
        flash('Name of project can not be empty')
        return redirect('/training')

    new_dataset = Dataset(user_id=session['user_id'], name=name)
    db.session.add(new_dataset)
    db.session.flush()
    filename = f'{new_dataset.dataset_id}_{secure_filename(file.filename)}'
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    new_dataset.dataset_filename = filename
    new_dataset.state = Dataset.UPLOADED
    db.session.commit()

    return redirect('/training')


@app.route('/delete-photo/<photo_id>', methods=['POST'])
def delete_pair(photo_id):
    photo = Photo.query.filter(Photo.photo_id == photo_id).first()
    if photo:
        if photo.original_photo:
            s3.delete(photo.original_photo)
        if photo.processed_photo:
            s3.delete(photo.processed_photo)
        db.session.delete(photo)
        db.session.commit()

    return ('', 200)


@app.route("/info")
def show_info():
    return render_template("about.html")


@app.route('/train-dataset/<dataset_id>', methods=['POST'])
def train_dataset(dataset_id):
    """Start training process"""

    dataset = Dataset.query.filter(Dataset.dataset_id == dataset_id).one()
    if dataset.state != Dataset.UPLOADED:
        raise ValueError("Dataset is not uploaded")
    dataset.state = Dataset.TRAINING_REQUESTED
    db.session.commit()
    return ('', 201)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = False

    connect_to_db(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(host="0.0.0.0")