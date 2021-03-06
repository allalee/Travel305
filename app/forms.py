from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField,SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
class SignupForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    dob = StringField("Date of Birth", validators=[DataRequired()],render_kw={"placeholder": "YYYY-MM-DD"})
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    gender = SelectField("Gender", choices=[('M','Male'),('F','Female')])
    submit = SubmitField("Sign Up")
class GroupNavForm(FlaskForm):
	createGroup = SubmitField("Create a Group")
	joinGroup = SubmitField("Join a Group")
class CreateGroup(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    name = StringField("Name (must match signup name)", validators=[DataRequired()])
    travelID = IntegerField("Enter a travel ID to identify your group", validators=[DataRequired()])
    submit = SubmitField("Submit")
class JoinGroup(FlaskForm):
    travelID = IntegerField("Enter the travel ID of the group you wish to join", validators=[DataRequired()])
    submit = SubmitField("Submit")
    leaveSubmit = SubmitField("Leave Current Group")
class Book(FlaskForm):
    duration = IntegerField("Enter Duration", validators=[DataRequired()])
    submit = SubmitField("Book This Trip")