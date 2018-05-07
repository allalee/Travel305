from flask import render_template, flash, redirect, url_for, request, json, jsonify
from app import app
from app.forms import LoginForm, SignupForm, GroupNavForm, CreateGroup, JoinGroup, Book
import flask_login
import pymysql.cursors
import sys

#Initialize the connection to the MYSQL server
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='Travel305',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

#User class for login and signup
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

# function returns the name of the user that is logged in
def getName():
    email = flask_login.current_user.get_id()
    cursor.execute("SELECT * FROM Users WHERE Email = \'" + email +  "\';")
    data = cursor.fetchall()
    name = data[0]["Name"]
    return name

# Landing page for the Travel305 website. It shows a few of everything that the service offers.
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

# Loads all accommodations into cards in a html file.
@app.route('/accommodations')
def accommodations():
    cursor.execute("SELECT * FROM Accommodation;")
    accommodations = cursor.fetchall()
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('accommodations.html', base_template = "base_loggedin.html", name = user_name, accommodations=accommodations)
    return render_template('accommodations.html', base_template = "base.html", accommodations=accommodations)

# Loads all cruises into cards in a html file.
@app.route('/cruises')
def cruises():
    cursor.execute("SELECT * FROM Cruise;")
    cruises = cursor.fetchall()
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('cruises.html', base_template = "base_loggedin.html", name = user_name, cruises=cruises)
    return render_template('cruises.html', base_template = "base.html", cruises=cruises)

# Loads all car rentals into cards in a html file.
@app.route('/carRentals')
def carRentals():
    cursor.execute("SELECT * FROM CarRental;")
    carRentals = cursor.fetchall()
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('carRentals.html', base_template = "base_loggedin.html", name = user_name, carRentals=carRentals)
    return render_template('carRentals.html', base_template = "base.html", carRentals=carRentals)

# Loads all flights into cards in a html file
@app.route('/flights')
def flights():
    cursor.execute("SELECT * FROM Flight;")
    flights = cursor.fetchall()
    if flask_login.current_user.is_authenticated:
        user_name = getName()
        return render_template('flights.html', base_template = "base_loggedin.html", name = user_name, flights=flights)
    return render_template('flights.html', base_template = "base.html", flights=flights)

# Collects login information from Flask Forms, validates the information and either fails or logs in.
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        cursor.execute("SELECT * FROM Users WHERE Email = \'" + email +  "\';")
        data = cursor.fetchall()
        if(len(data) == 0):
            flash("Invalid email or password", 'danger')
            return redirect(url_for('login'))
        if(data[0]["Password"] != password):
            flash("Invalid email or password", 'danger')
            return redirect(url_for('login'))
        if(data[0]["Email"] == email and data[0]["Password"] == password):
            user = User(data[0]["Email"])
            flask_login.login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', title="Login", form=form, loggedin = False)

# Logs user out and returns to the index page.
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))

# Collects information from Flask forms and creates a new user in the users table of the database.
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
        flash("You have successfully signed up! Log in to access our service!", 'success')
        return render_template('signupcomplete.html')
    return render_template('signup.html', title="Signup", form=form)

# Shows all available locations that can be added to a trip.
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

# Group home page that gives user the option to create or join group.
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

# Creates a new group in the database, and by default adds the user creating the group into the group.
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
            flash("Account does not exist", 'danger')
            redirect(url_for("createGroup"))
        else:
            cursor.execute("SELECT * FROM `Group` WHERE TravelID = " + str(travelID) + ";")
            data = cursor.fetchall()
            if len(data) != 0:
                flash("Travel ID already exists. Enter another value", 'danger')
                redirect(url_for("createGroup"))
            else:
                sql = "INSERT INTO `Group` VALUES (NULL, " + str(travelID) + ", 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL);"
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
                flash("Group has been created under ID: " + str(travelID),'success')
                redirect(url_for("createGroup"))
    return render_template('creategroup.html', name = username, form = form)

# User joins a group with a valid group ID.
def joinGroupFunction(ID, travelID):
    sql = "SELECT GroupID FROM `Group` WHERE TravelID = " + str(travelID) + ";"
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("That is not a valid travel ID",'danger')
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

# User is deleted from the specific group in the group table.
def leaveGroupFunction(ID):
    sql = "SELECT PassengerID FROM PartOf WHERE PassengerID = " + str(ID) + ";"
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("You are not in a group!", 'danger')
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

# User can join group and a unique html file is displayed.
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
                flash("You are already in a group! Leave your group first.", 'danger')
                redirect_option = False
            elif desired_travel_id == None:
                flash("That is not a valid travel ID", 'danger')
                redirect_option = False
            else:
                redirect_option = joinGroupFunction(ID, desired_travel_id)
        else:
            redirect_option = leaveGroupFunction(ID)
        if redirect_option:
            return redirect(url_for('index'))
    return render_template('joingroup.html', name = username, form = form, groups = groupData, group_status = group_status, travelID = travelID)

# User picks a source location for their groups trip and the group table is updated.
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

# User picks a destination location for their groups trip and the group table is updated.
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

# User can add any form of transportation to their trip.
def addTransport(ID, groupID, travelType):
    tid =str(ID)
    print("THE ID IS: " + tid, file=sys.stdout)
    print(travelType, file=sys.stdout)
    sql = "SELECT TransportationType FROM Transportation WHERE TransportationID = " + str(ID) + ";"
    cursor.execute(sql)
    transport = cursor.fetchall()
    transport = transport[0]["TransportationType"]
    sql = "UPDATE `Group` SET ModeOfTransport = \'" + transport + "\' WHERE GroupID = " + str(groupID) + ";"
    cursor.execute(sql)
    cost = ""
    if travelType=="Flight":
        sql = "SELECT Fare FROM Flight WHERE FlightNumber = " + str(ID) + ";"
        cost="Fare"
    elif travelType=="Cruise":
        sql = "SELECT Fare FROM Cruise WHERE CruiseNumber = " + str(ID) + ";"
        cost ="Fare"
    elif travelType=="CarRental":
        sql = "SELECT Rent FROM CarRental WHERE CarRentalConfirmationID = " + str(ID) + ";"
        cost="Rent"
    cursor.execute(sql)
    transportCost = cursor.fetchone()[cost]
    print(transportCost, file=sys.stdout)
    sql = "UPDATE `Group` SET TransportCost = \'" + str(transportCost) + "\' WHERE GroupID = " + str(groupID) + ";"
    cursor.execute(sql)
    connection.commit()

#Accommodation is currently being stored in the Purpose field of the Group table!
def addAccommodation(accommodation, groupid, facilities, rate, discount):
    sql = "UPDATE `Group` SET Accommodation = \'%s:%s:%s:%s\' WHERE GroupID = %s;" % (str(accommodation), str(facilities), rate.strip("/"), discount.strip("/"), str(groupid))
    cursor.execute(sql)
    connection.commit()

# Handles a request to add anything to the group.
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
                addTransport(request.form['addCruise'], data[0]["GroupID"], "Cruise")
            elif 'addAccommodation' in request.form:
                addAccommodation(request.form['addAccommodation'], data[0]["GroupID"], request.form['Facilities'], request.form['Rate'], request.form['Discount'])
            elif 'addCarRental' in request.form:
                addTransport(request.form['addCarRental'], data[0]["GroupID"], "CarRental")
            elif 'addFlight' in request.form:
                addTransport(request.form['addFlight'], data[0]["GroupID"], "Flight")
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
    print(data,file=sys.stdout)
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
            flash("You have not selected enough information to book this trip!", 'danger')
        else:
            v = booking_parse_accommodation(items[0]["Accommodation"])
            sql = "SELECT TransportCost FROM `Group` WHERE GroupID = \'%s\';" % (str(ID))
            cursor.execute(sql)
            transport_cost = cursor.fetchone()["TransportCost"]
            print(transport_cost,file=sys.stdout)
            accommodation_cost = v[2]
            discount = v[3]
            total_cost = (int(form.duration.data) * int(accommodation_cost)) - int(discount) + int(transport_cost)
            total_accommodation_cost = (int(form.duration.data)*int(accommodation_cost))
            print(total_cost, file=sys.stdout)
            sql = "INSERT INTO Books VALUES (%s,%s,\'%s\',\'%s\',%s);" % (str(items[0]["GroupID"]), str(form.duration.data), v[0], v[1], str(total_cost))
            cursor.execute(sql)
            connection.commit()
            return render_template("bookedtrips.html",base_template="base_loggedin.html",accommodation_cost=accommodation_cost,
                discount=discount, transport_cost=transport_cost,total_cost=total_cost,total_accommodation_cost=total_accommodation_cost, duration=str(form.duration.data), name=getName())
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
