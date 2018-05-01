from flask import render_template, flash, redirect, url_for, request, json, jsonify
from app import app
from app.forms import LoginForm, SignupForm, GroupNavForm, CreateGroup, JoinGroup
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
        self.email = None
    def __repr__(self):
        return self.id
    def addEmail(self, email):
        self.email = email
    def email(self):
        return self.email

@login_manager.user_loader
def load_user(userid):
    return User(userid)

def getName():
    email = flask_login.current_user.get_id()
    cursor.execute("SELECT * FROM Users WHERE Email = \'" + email +  "\';")
    data = cursor.fetchall()
    name = data[0]["Name"]
    return name

@app.route('/')
@app.route('/index')
def index():
    cursor.execute("SELECT * FROM Location;")
    locations = cursor.fetchmany(4)
    cursor.execute("SELECT * FROM Cruise;")
    cruises = cursor.fetchmany(4)
    cursor.execute("SELECT * FROM Accommodation;")
    accommodations = cursor.fetchmany(4)
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('index.html', base_template = "base_loggedin.html", name = user_name, locations=locations, cruises=cruises, accommodations=accommodations)
    return render_template('index.html', base_template = "base.html", locations=locations, cruises=cruises, accommodations=accommodations)


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
            user = User(data[0]["Email"])
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
        username = getName()
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
    username = getName()
    if form.is_submitted():
        if 'createGroup' in request.form:
            return redirect(url_for("createGroup"))
        if 'joinGroup' in request.form:
            return redirect(url_for("joinGroup"))
    return render_template('grouphome.html', name = username, form = form)

@app.route('/creategroup', methods=['GET','POST'])
def createGroup():
    form = CreateGroup()
    username = getName()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        travelID = form.travelID.data
        cursor.execute("SELECT * FROM Users WHERE Email = \'" + email + "\' AND Name = \'" + name + "\';")
        data = cursor.fetchall()
        if len(data) == 0:
            flash("Account does not exist")
            redirect(url_for("createGroup"))
        else:
            cursor.execute("SELECT * FROM `Group` WHERE TravelID = " + str(travelID) + ";")
            data = cursor.fetchall()
            if len(data) != 0:
                flash("Travel ID already exists. Enter another value")
                redirect(url_for("createGroup"))
            else:
                sql = "INSERT INTO `Group` VALUES (NULL, " + str(travelID) + ", 1, NULL, NULL, NULL, NULL);"
                cursor.execute(sql)
                connection.commit()
                sql = "SELECT * FROM Users WHERE Email = \'" + email + "\';"
                cursor.execute(sql)
                data = cursor.fetchall()
                PassengerID = data[0]["ID"]
                sql = "SELECT * FROM `Group` WHERE travelID = " + str(travelID) + ";"
                cursor.execute(sql)
                data = cursor.fetchall()
                groupID = data[0]["GroupID"]
                sql = "INSERT INTO PartOf VALUES (" + str(PassengerID) + ", " + str(groupID) + ");"
                cursor.execute(sql)
                connection.commit()
                flash("Group has been created under ID: " + str(travelID))
                redirect(url_for("createGroup"))
    return render_template('creategroup.html', name = username, form = form)

def joinGroupFunction(ID, travelID):
    sql = "SELECT GroupID FROM `Group` WHERE TravelID = " + str(travelID) + ";"
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("That is not a valid travel ID")
        return False
    else:
        sql = "INSERT INTO PartOf VALUES (" + str(ID) + ", " + str(data[0]["GroupID"]) + ");"
        cursor.execute(sql)
        connection.commit()
        sql = "SELECT GroupSize FROM `Group` WHERE GroupID = " + str(data[0]["GroupID"]) + ";"
        cursor.execute(sql)
        group_data = cursor.fetchall()
        group_size = group_data[0]["GroupSize"]
        group_size = int(group_size) + 1
        sql = "UPDATE `Group` SET GroupSize = " + str(group_size) + " WHERE GroupID = " + str(data[0]["GroupID"]) + ";"
        cursor.execute(sql)
        connection.commit()
        return True

def leaveGroupFunction(ID):
    sql = "SELECT PassengerID FROM PartOf WHERE PassengerID = " + str(ID) + ";"
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("You are not in a group!")
        return False
    else:
        sql = "SELECT GroupID FROM PartOf WHERE PassengerID = " + str(ID) + ";"
        cursor.execute(sql)
        group_id = cursor.fetchall()
        sql = "SELECT GroupSize FROM `Group` WHERE GroupID = " + str(group_id[0]["GroupID"]) + ";"
        cursor.execute(sql)
        group_data = cursor.fetchall()
        group_size = group_data[0]["GroupSize"]
        group_size = int(group_size) - 1
        sql = "UPDATE `Group` SET GroupSize = " + str(group_size) + " WHERE GroupID = " + str(group_id[0]["GroupID"]) + ";"
        cursor.execute(sql)
        connection.commit()
        sql = "DELETE FROM PartOf WHERE PassengerID = " + str(ID) + ";"
        cursor.execute(sql)
        connection.commit()
        return True

@app.route('/joingroup', methods=['GET','POST'])
def joinGroup():
    form = JoinGroup()
    username = getName()
    email = flask_login.current_user.get_id()
    sql = "SELECT ID FROM Users WHERE Email = \'" + email + "\';"
    cursor.execute(sql)
    data = cursor.fetchall()
    ID = data[0]["ID"]
    sql = "SELECT * FROM PartOf WHERE PassengerID = " + str(ID) + ";"
    cursor.execute(sql)
    data = cursor.fetchall()
    sql = "SELECT * FROM `Group`;"
    cursor.execute(sql)
    groupData = cursor.fetchall()
    if len(data) == 0:
        travelID = None
        group_status = False
    else:
        groupID = data[0]["GroupID"]
        sql = "SELECT * FROM `Group` WHERE GroupID = " + str(groupID) + ";"
        cursor.execute(sql)
        data = cursor.fetchall()
        travelID = data[0]["TravelID"]
        group_status = True
    if form.is_submitted():
        if 'submit' in request.form:
            desired_travel_id = form.travelID.data
            if travelID != None:
                flash("You are already in a group! Leave your group first.")
                redirect_option = False
            elif desired_travel_id == None:
                flash("That is not a valid travel ID")
                redirect_option = False
            else:
                redirect_option = joinGroupFunction(ID, desired_travel_id)
        else:
            redirect_option = leaveGroupFunction(ID)
        if redirect_option:
            return redirect(url_for('index'))
    return render_template('joingroup.html', name = username, form = form, groups = groupData, group_status = group_status, travelID = travelID)

@app.route('/addToCart', methods=['POST'])
def addToCart():
    redirect_option = False
    selected = True
    if flask_login.current_user.is_authenticated:
        email = flask_login.current_user.get_id()
        sql = "SELECT ID FROM Users WHERE Email = \'" + email + "\';"
        cursor.execute(sql)
        data = cursor.fetchall()
        ID = data[0]["ID"]
        sql = "SELECT GroupID FROM PartOf WHERE PassengerID = " + str(ID) + ";"
        cursor.execute(sql)
        data = cursor.fetchall()
        if len(data) == 0:
            return redirect(url_for('booking'))
        else:
            if 'makeSource' in request.form:
                print("makeSource")
            elif 'makeDest' in request.form:
                print("makeDest")
            elif 'addCruise' in request.form:
                print("addCruise")
            elif 'addAccommodation' in request.form:
                print("addAcc")
    else:
        selected = False
        redirect_option = True
    if redirect_option:
        return redirect(url_for('mustBeLogged'))
    if selected:
        return redirect(url_for('booking'))

@app.route('/mustBeLogged', methods=['GET','POST'])
def mustBeLogged():
    return render_template('mustbelogged.html')

@app.route('/booking', methods=['GET','POST'])
def booking():
    user_name = getName()
    email = flask_login.current_user.get_id()
    sql = "SELECT ID FROM Users WHERE Email = \'" + email + "\';"
    cursor.execute(sql)
    data = cursor.fetchall()
    ID = data[0]["ID"]
    sql = "SELECT GroupID FROM PartOf WHERE PassengerID = " + str(ID) + ";"
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) == 0:
        groupInfo = ()
        val = True
    else:
        groupID = data[0]["GroupID"]   
        sql = "SELECT * FROM `Group` WHERE GroupID = " + str(groupID) + ";"
        cursor.execute(sql)
        groupInfo = cursor.fetchall()
        val = False
    return render_template('booking.html', base_template = "base_loggedin.html", name = user_name, group = groupInfo, val = val)
