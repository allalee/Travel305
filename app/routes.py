from flask import render_template, flash, redirect, url_for, request, json, jsonify
from app import app
from app.forms import LoginForm, SignupForm, GroupNavForm
import flask_login
import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='Travel305',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
class User(flask_login.UserMixin):
    def __init__(self, id):
        self.id = id
    def __repr__(self):
        return self.id
@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route('/')
@app.route('/index')
def index():
    if flask_login.current_user.is_authenticated:
        user_name = flask_login.current_user.get_id()
        return render_template('index.html', base_template = "base_loggedin.html", name = user_name)
    return render_template('index.html', base_template = "base.html")


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        cursor.execute("SELECT * FROM Users WHERE Email = \'" + email +  "\';")
        data = cursor.fetchall()
        if(len(data) == 0):
            flash("Invalid email or password")
            return redirect(url_for('login'))
        if(data[0]["Password"] != password):
            flash("Invalid email or password")
            return redirect(url_for('login'))
        if(data[0]["Email"] == email and data[0]["Password"] == password):
            user = User(data[0]["Name"])
            flask_login.login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', title="Login", form=form, loggedin = False)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))

@app.route('/signup',methods=["POST","GET"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        dob=form.dob.data
        email=form.email.data
        password=form.password.data
        gender=form.gender.data
        sql="INSERT INTO Users VALUES (NULL,"+"\'"+email+"\',"+"\'"+name+"\',"+"\'"+password+"\',"+'\''+gender+'\','+'\''+dob+'\')'
        cursor.execute(sql)
        connection.commit()
        return render_template('signupcomplete.html')
    return render_template('signup.html', title="Signup", form=form)

@app.route('/locations')
def showLocations():
    if flask_login.current_user.is_authenticated:
        username = flask_login.current_user.get_id()
        base_template = "base_loggedin.html"
    else:
        username = ""
        base_template = "base.html"
    sql = "SELECT * FROM Location;"
    cursor.execute("SELECT * FROM Location;")
    locations = cursor.fetchall()
    return render_template('locations.html', title="Locations", locations=locations, base_template = base_template, name = username)

# @app.route('/accommodations', methods=['GET','POST'])
# @app.route('/flights', methods=['GET','POST'])
# @app.route('/carrentals', methods=['GET','POST'])
# @app.route('/review', methods=['GET','POST'])

@app.route('/grouphome', methods=['GET','POST'])
def groupHome():
    form = GroupNavForm()
    username = flask_login.current_user.get_id()
    if form.is_submitted():
        if 'createGroup' in request.form:
            print("Y")
    return render_template('grouphome.html', name = username, form = form)