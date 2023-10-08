from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,DecimalField, HiddenField,BooleanField,IntegerField,SubmitField
from wtforms.validators import InputRequired,Length,Email,DataRequired
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(),Length(min=4,max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    username =  StringField('username', validators=[InputRequired(),Length(min=4,max=15)])
    password =  PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
    email =     StringField('email',validators=[InputRequired(),Email(message='Invalid email'),Length(max=100)])

class AddPropertyForm(FlaskForm):
    address =       StringField('Address', validators=[InputRequired(),Length(max=100)])
    purch_price =   DecimalField('Purchase Price (with closing cost)',validators=[InputRequired()])
    est_rent =      DecimalField('Estimated Rent',validators=[InputRequired()])
    image =         StringField("Image URL **Optional")

class AddImageForm(FlaskForm):
    imageURL = StringField("Image URL")

class IncomeForm(FlaskForm):
    income_amt =        DecimalField("Income Amount")
    income_name =       StringField("Income Name")

class ExpenseForm(FlaskForm):
    expense_amt =       DecimalField("Expense Amount")
    expense_name =      StringField("Expense Name")

class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[ DataRequired()])
    image = StringField("Img Url **Optional",render_kw={'placeholder':'optional'})
    description = StringField("Description **Optional")
    price = DecimalField("Price", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField()

class UserAccountForm(FlaskForm):
    username =          StringField('Username')
    first_name =        StringField('First Name')
    last_name =         StringField('Last Name')
    address =           StringField('Address')
    city =              StringField('City')
    state =             StringField('State')
    zip =               StringField('Postal Code')
    email =             StringField('Email')
    phone =             StringField('Phone')
    about_me_label =    StringField(u"About Me")
    about_me_body =     StringField(u'About Me', widget=TextArea())