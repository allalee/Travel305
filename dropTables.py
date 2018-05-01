import pymysql as pymysql

# run mysql -u root -p
# databases are stored in /var/lib/mysql
# Deleting a database is DROP DATABASE <db name>
# Describe <Table name>;

# Connect to the database via pymysql library using localhost 127.0.0.1 and port 3306
# The user is 'root' and db is whatever db we are using. password is nickcastro12 (Local to your machine)
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', db='Travel305', password='password')
cursor = conn.cursor() # Cursor object is what we will use to execute commands

cursor.execute("ALTER TABLE Passengers DROP FOREIGN KEY PassengersPartOf;")
# cursor.execute("ALTER TABLE Passengers DROP FOREIGN KEY PassengersPayment;")
# cursor.execute("ALTER TABLE `Group` DROP FOREIGN KEY GroupID;")
# cursor.execute("ALTER TABLE `Group` DROP FOREIGN KEY TravelID;")

TableList = ["Travels", "Makes", "Writes", "Books", "PartOf", "Cruise", "Flight", "CarRental", "Employee", 
	"Accommodation", "`Group`", "Transportation", "Location", "Review", "Payment", "Passengers", "Users"]

for table in TableList:
	cursor.execute("drop table " + table + ";")

