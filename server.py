from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask import url_for, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Photo


import os

from werkzeug.utils import secure_filename

import subprocess



UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raise an error if there is undefined variable in Jinja2.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/signin', methods= ['POST'])
def signin():
    """Check if user exists. Redirect to the library"""

    email = request.form.get('email')
    password = request.form.get('password')



    user = User.query.filter(User.email==email).one()

    if not user:
        flash("No such user")
        

        return redirect("/")

    if user.password != password:

        flash("Incorrect password")
        return redirect("/")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/library")


@app.route('/login', methods= ['POST'])
def login():
    """Add info about new user in a database. Log in a new user"""

    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')

    new_user = User(email=email, password=password, name = name)
    db.session.add(new_user)
    db.session.commit()

    #add new user to the session
    new_user = User.query.filter(User.email==email).one()
    session['user_id'] = new_user.user_id

    flash("User {} added.".format(name))
    return redirect("/library")

@app.route("/library")
def user_detail():
    """Show user's library."""

    user_id = session.get("user_id")

    #Checking if the user is logged in a system.
    if user_id:
        user = User.query.get(user_id)
        photos = Photo.query.filter(Photo.user_id==user_id).all()
        return render_template("library.html", user=user, photos=photos)

    #if user is not logged in send him back to the homepage
    else:
        flash("You are not logged in.")
        return redirect('/')

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    if file and allowed_file(file.filename):
        new_photo = Photo(user_id=session['user_id'])
        db.session.add(new_photo)
        db.session.flush()

        filename = f'{new_photo.photo_id}_{secure_filename(file.filename)}'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_photo.original_photo = filename
        db.session.commit()

        return redirect(f'/processing/{new_photo.photo_id}')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/processing/<photo_id>')
def photo_processing(photo_id):
    """Photo processing page"""

    photo = Photo.query.filter(
        Photo.user_id == session['user_id'],
        Photo.photo_id == photo_id,
    ).first()


    return render_template("processing.html", photo=photo)


@app.route('/process/<photo_id>', methods=['POST'])
def process_photo(photo_id):
    """Convert photo"""

    photo = Photo.query.filter(
        Photo.user_id == session['user_id'],
        Photo.photo_id == photo_id,
    ).first()

    processed_photo = f'new_{photo.original_photo}'
    original_path = os.path.join(UPLOAD_FOLDER, photo.original_photo)
    processed_path = os.path.join(UPLOAD_FOLDER, processed_photo)

    completed = subprocess.run([
        'convert', original_path, '-set', 'colorspace', 'Gray', processed_path
    ], stdout=subprocess.PIPE, check=True)

    photo.processed_photo = processed_photo
    db.session.commit()

    url=url_for('uploaded_file', filename=photo.processed_photo)
    return url;





if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(host="0.0.0.0")