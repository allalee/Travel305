import pymysql as pymysql

# run mysql -u root -p
# databases are stored in /var/lib/mysql
# Deleting a database is DROP DATABASE <db name>
# Describe <Table name>;
# Have backticks on all attribute names to avoid conflicts with reserved key words

# Connect to the database via pymysql library using localhost 127.0.0.1 and port 3306
# The user is 'root' and db is whatever db we are using. password is nickcastro12 (Local to your machine)
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', db='Travel305', password='password')
cursor = conn.cursor() # Cursor object is what we will use to execute commands

# Example code
# cursor.execute("SHOW TABLES LIKE \"Person\"")
# tables = cursor.fetchall()
# print(tables)
# print("This is a very long"
# 	"String")

# The following initiliazes the database with the tables
initUserTable = "CREATE TABLE Users (ID int not null auto_increment,"\
"Email varchar(100),"\
"Name varchar(30),"\
"Password varchar(20),"\
"Gender char(1),"\
"DateOfBirth date,"\
"primary key (ID));"

initPassengerTable = "CREATE TABLE Passengers (PassengerID int,"\
"PaymentID int,"\
"PassengerName varchar(30),"\
"Gender char(1),"\
"Age int,"\
"primary key (PassengerID),"\
"foreign key (PassengerID) references Users(ID));"

initPaymentTable = "CREATE TABLE Payment (PaymentType varchar(50),"\
"PaymentNumber int,"\
"CardNumber varchar(50),"\
"CardExpiryDate date,"\
"primary key (PaymentNumber, CardNumber, CardExpiryDate));"

initReviewTable = "CREATE TABLE Review (PassengerID int,"\
"Ratings int,"\
"`Group` int,"\
"DetailedReview varchar(1000) not null,"\
"primary key (PassengerID));"

initLocationTable = "CREATE TABLE Location (LocationID int,"\
"CityName varchar(255),"\
"Country varchar(255),"\
"State varchar(255),"\
"ImgDir varchar(255),"\
"primary key (LocationID));"

initTransportationTable = "CREATE TABLE Transportation (TransportationID int,"\
"TransportationType varchar(255),"\
"ClassType varchar(255),"\
"primary key (TransportationID));"

initGroupTable = "CREATE TABLE `Group` (GroupID int auto_increment,"\
"TravelID int,"\
"`GroupSize` int,"\
"SourceLocation int,"\
"`DestinationLocation` int,"\
"ModeOfTransport varchar(255),"\
"Purpose varchar(1000),"\
"primary key (GroupID),"\
"foreign key (SourceLocation) references Location(LocationID),"\
"foreign key (DestinationLocation) references Location(LocationID));"\

initAccommodationTable = "CREATE TABLE Accommodation (AccommodationType varchar(255),"\
"Facilities varchar(255),"\
"RatePerNight int,"\
"Discount int,"\
"ImgDir varchar(255),"\
"primary key (AccommodationType, Facilities));"

initEmployeeTable = "CREATE TABLE Employee (EmployeeID int,"\
"Designation varchar(255),"\
"Facilities varchar(255),"\
"SupervisorID int,"\
"primary key (EmployeeID));"\
# "foreign key (SupervisorID) references (EmployeeID));"

initCarRental = "CREATE TABLE CarRental (CarRentalConfirmationID int,"\
"CarType varchar(255),"\
"Rent int,"\
"ImgDir varchar(255),"\
"primary key (CarRentalConfirmationID),"\
"foreign key (CarRentalConfirmationID) references Transportation(TransportationID));"

initFlightTable = "CREATE TABLE Flight (FlightNumber int,"\
"FlightCarrier varchar(255),"\
"SourceLocation varchar(255),"\
"DestinationLocation varchar(255),"\
"Class varchar(100),"\
"Fare int,"\
"primary key (FlightNumber),"\
"foreign key (FlightNumber) references Transportation(TransportationID));"

initCruiseTable = "CREATE TABLE Cruise (CruiseNumber int,"\
"SourceLocation varchar(255),"\
"DestinationLocation varchar(255),"\
"Fare int,"\
"primary key (CruiseNumber),"\
"foreign key (CruiseNumber) references Transportation(TransportationID));"

initPartOfTable = "CREATE TABLE PartOf (PassengerID int,"\
"GroupID int,"\
"primary key (PassengerID),"\
"foreign key (GroupID) references `Group`(GroupID));"

initBooksTable = "CREATE TABLE Books (GroupID int,"\
"ForDuration varchar(255),"\
"AccommodationType varchar(255),"\
"Facilities varchar(255),"\
"primary key (GroupID),"\
"foreign key (AccommodationType, Facilities) references Accommodation(AccommodationType, Facilities));"

initWritesTable = "CREATE TABLE Writes (PassengerID int,"\
"DetailedReview int,"\
"primary key (PassengerID),"\
"foreign key (PassengerID) references Passengers(PassengerID));"\
# "foreign key (DetailedReview) references Review(DetailedReview));"

initMakesTable = "CREATE TABLE Makes (PassengerID int,"\
"PaymentID int,"\
"Paid float,"\
"AmountLeft float,"\
"PaymentNumber int,"\
"CardNumber varchar(50),"\
"CardExpiryDate date,"\
"primary key (PassengerID),"\
"foreign key (PaymentNumber, CardNumber, CardExpiryDate) references Payment(PaymentNumber, CardNumber, CardExpiryDate));"

initTravelsTable = "CREATE TABLE Travels (TravelID int,"\
"SourceLocation int,"\
"DestinationLocation int,"\
"primary key (TravelID),"\
"foreign key (SourceLocation) references Location(LocationID),"\
"foreign key (DestinationLocation) references Location(LocationID));"

initTable = [initUserTable, initPassengerTable, initPaymentTable, initReviewTable, initLocationTable, initTransportationTable, initGroupTable, initAccommodationTable, initEmployeeTable, initCarRental,
	initFlightTable, initCruiseTable, initPartOfTable, initBooksTable, initWritesTable, initMakesTable, initTravelsTable]
for table in initTable:
	cursor.execute(table)

alterP1 = "ALTER TABLE Passengers ADD CONSTRAINT PassengersPartOf FOREIGN KEY (PassengerID) REFERENCES PartOf(PassengerID);"
# alterP2 = "ALTER TABLE Passengers ADD CONSTRAINT PassengersPayment FOREIGN KEY (PaymentID) REFERENCES Makes(PaymentID) ON DELETE CASCADE ON UPDATE CASCADE;"
# alterP3 = "ALTER TABLE `Group` ADD CONSTRAINT GroupID FOREIGN KEY (GroupID) REFERENCES Books(GroupID);"
# alterP4 = "ALTER TABLE `Group` ADD CONSTRAINT TravelID FOREIGN KEY (TravelID) REFERENCES Travels(TravelID);"
alterTable = [alterP1]
for alter in alterTable:
	cursor.execute(alter)
