from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Photo


app = Flask(__name__)

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



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")