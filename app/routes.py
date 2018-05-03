from flask import render_template, flash, redirect, url_for, request, json, jsonify
from app import app
from app.forms import LoginForm, SignupForm, GroupNavForm, CreateGroup, JoinGroup, Book
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
    cursor.execute("SELECT * FROM Flight;")
    flights = cursor.fetchmany(4)
    cursor.execute("SELECT * FROM CarRental;")
    carRentals=cursor.fetchmany(4)
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('index.html', base_template = "base_loggedin.html", name = user_name, locations=locations, cruises=cruises, accommodations=accommodations, flights=flights,carRentals=carRentals)
    return render_template('index.html', base_template = "base.html", locations=locations, cruises=cruises, accommodations=accommodations, flights=flights,carRentals=carRentals)

@app.route('/accommodations')
def accommodations():
    cursor.execute("SELECT * FROM Accommodation;")
    accommodations = cursor.fetchall()
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('accommodations.html', base_template = "base_loggedin.html", name = user_name, accommodations=accommodations)
    return render_template('accommodations.html', base_template = "base.html", accommodations=accommodations)

@app.route('/cruises')
def cruises():
    cursor.execute("SELECT * FROM Cruise;")
    cruises = cursor.fetchall()
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('cruises.html', base_template = "base_loggedin.html", name = user_name, cruises=cruises)
    return render_template('cruises.html', base_template = "base.html", cruises=cruises)

@app.route('/carRentals')
def carRentals():
    cursor.execute("SELECT * FROM CarRental;")
    carRentals = cursor.fetchall()
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('carRentals.html', base_template = "base_loggedin.html", name = user_name, carRentals=carRentals)
    return render_template('cruises.html', base_template = "base.html", carRentals=carRentals)

@app.route('/flights')
def flights():
    cursor.execute("SELECT * FROM Flight;")
    flights = cursor.fetchall()
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('flights.html', base_template = "base_loggedin.html", name = user_name, flights=flights)
    return render_template('flights.html', base_template = "base.html", flights=flights)

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
                sql = "INSERT INTO `Group` VALUES (NULL, " + str(travelID) + ", 1, NULL, NULL, NULL, NULL, NULL, NULL);"
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


def makeSource(ID, groupID):
    sql = "UPDATE `Group` SET SourceLocation = " + str(ID) + " WHERE GroupID = " + str(groupID) + ";"
    cursor.execute(sql)
    connection.commit()
    sql = "SELECT CityName FROM Location WHERE LocationID = " + str(ID) + ";"
    cursor.execute(sql)
    cityName = cursor.fetchall()
    cityName = cityName[0]["CityName"]
    sql = "UPDATE `Group` SET SrcName = \'" + cityName + "\' WHERE GroupID = " + str(groupID) + ";"
    cursor.execute(sql)
    connection.commit()

def makeDest(ID, groupID):
    sql = "UPDATE `Group` SET DestinationLocation = " + str(ID) + " WHERE GroupID = " + str(groupID) + ";"
    cursor.execute(sql)
    connection.commit()
    sql = "SELECT CityName FROM Location WHERE LocationID = " + str(ID) + ";"
    cursor.execute(sql)
    cityName = cursor.fetchall()
    cityName = cityName[0]["CityName"]
    sql = "UPDATE `Group` SET DestName = \'" + cityName + "\' WHERE GroupID = " + str(groupID) + ";"
    cursor.execute(sql)
    connection.commit()

def addTransport(ID, groupID):
    sql = "SELECT TransportationType FROM Transportation WHERE TransportationID = " + str(ID) + ";"
    cursor.execute(sql)
    transport = cursor.fetchall()
    transport = transport[0]["TransportationType"]
    sql = "UPDATE `Group` SET ModeOfTransport = \'" + transport + "\' WHERE GroupID = " + str(groupID) + ";"
    cursor.execute(sql)
    connection.commit()

#Accommodation is currently being stored in the Purpose field of the Group table!
def addAccommodation(accommodation, groupid, facilities, rate, discount):
    sql = "UPDATE `Group` SET Accommodation = \'%s:%s:%s:%s\' WHERE GroupID = %s;" % (str(accommodation), str(facilities), rate.strip("/"), discount.strip("/"), str(groupid))
    cursor.execute(sql)
    connection.commit()

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
                makeSource(request.form['makeSource'], data[0]["GroupID"])
            elif 'makeDest' in request.form:
                makeDest(request.form['makeDest'], data[0]["GroupID"])
            elif 'addCruise' in request.form:
                addTransport(request.form['addCruise'], data[0]["GroupID"])
            elif 'addAccommodation' in request.form:
                addAccommodation(request.form['addAccommodation'], data[0]["GroupID"], request.form['Facilities'], request.form['Rate'], request.form['Discount'])
            elif 'addCarRental' in request.form:
                addTransport(request.form['addCarRental'], data[0]["GroupID"])
            elif 'addFlight' in request.form:
                addTransport(request.form['addFlight'], data[0]["GroupID"])
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

def booking_parse_accommodation(acc):
    if acc == None:
        return None
    else:
        lst = acc.split(":")
        return lst

@app.route('/booking', methods=['GET','POST'])
def booking():
    form = Book()
    user_name = getName()
    email = flask_login.current_user.get_id()
    sql = "SELECT ID FROM Users WHERE Email = \'" + email + "\';"
    cursor.execute(sql)
    data = cursor.fetchall()
    ID = data[0]["ID"]
    sql = "SELECT GroupID FROM PartOf WHERE PassengerID = " + str(ID) + ";"
    cursor.execute(sql)
    data = cursor.fetchall()
    if form.is_submitted():
        sql = "SELECT * FROM `Group` WHERE GroupID = \'%s\';" % (str(ID))
        cursor.execute(sql)
        items = cursor.fetchall()
        f = False
        for key, val in items[0].items():
            if val == None:
                f = True
                break
        if f or form.duration.data == None:
            flash("You have not selected enough information to book this trip!")
        else:
            v = booking_parse_accommodation(items[0]["Accommodation"])
            sql = "INSERT INTO Books VALUES (%s,%s,\'%s\',\'%s\');" % (str(items[0]["GroupID"]), str(form.duration.data), v[0], v[1])
            cursor.execute(sql)
            connection.commit()
            return redirect(url_for("booked_trips"))
    if len(data) == 0:
        groupInfo = ()
        acc = None
        val = True
    else:
        groupID = data[0]["GroupID"]
        sql = "SELECT * FROM `Group` WHERE GroupID = " + str(groupID) + ";"
        cursor.execute(sql)
        groupInfo = cursor.fetchall()
        acc = booking_parse_accommodation(groupInfo[0]['Accommodation'])
        val = False
    return render_template('booking.html', base_template = "base_loggedin.html", name = user_name, group = groupInfo, val = val, acc = acc, form = form)

@app.route('/bookedtrips', methods=['GET','POST'])
def booked_trips():
    #MUST CHECK IF WE BOOKED A TRIP AND DISPLAY IN TABLE
    return render_template('bookedtrips.html', base_template = "base_loggedin.html")
