from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, String, Integer,DateTime,UniqueConstraint,ForeignKey,Text,text,Numeric
from flask_login import UserMixin,LoginManager
from datetime import datetime
import bcrypt
from flask_marshmallow import Marshmallow

db=SQLAlchemy()

login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

ma = Marshmallow()


class Users(db.Model,UserMixin):
    __tablename__ = "users"
    user_id =           Column("user_id", Integer,primary_key=True,autoincrement=True)
    first_name =        Column("fname",Text,default="none")
    last_name =         Column("lname",Text,default="none")
    email =             Column("email",Text,unique=True,nullable=False)
    phone =             Column("phone",Text,default="none")
    username =          Column("username",Text,unique=True,nullable=False)
    password =          Column("pwd",Text,nullable=False)
    created_on =        Column("created_on", DateTime(timezone=True),default=datetime.now())

    def __init__(self, email, password,username):
        self.first_name = ""
        self.last_name = ""
        self.email = email
        self.phone = ""
        self.password = password
        self.username = username


    def pass_hash(password):
        hash_pwd = bcrypt.generate_password_hash(password)
        return hash_pwd
    
    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"User: {self.first_name} {self.last_name} Email: {self.email} Phone: {self.phone} User ID: {self.user_id} password: {self.password} "

class Property(db.Model):
    __tablename__ =         "property"
    prop_id =               Column(Integer, primary_key=True,autoincrement=True)
    address =               Column(Text,default='none')
    purch_price =           Column(Numeric(10,2),default=0)
    est_rent =              Column(Numeric(10,2),default=0)
    user_id =               Column(Integer,ForeignKey('users.user_id'))
    

class Income(db.Model):
    __tablename__ =         "income"
    inc_id =                Column("inc_id",Integer, primary_key=True,autoincrement=True)
    prop_id =               Column("prop_id",Integer,ForeignKey('property.prop_id'))
    name =                  Column("name",Text,default = "")
    amount =                Column("amount",Numeric(10,2),default=0)
    user_id =               Column(Integer,ForeignKey('users.user_id'))

    def __init__(self, prop_id, name,amount,user_id):
        self.prop_id = prop_id
        self.name = name
        self.amount = amount
        self.user_id = user_id

     
class Expenses(db.Model):
    __tablename__ =         "expense"
    exp_id =                Column("inc_id",Integer, primary_key=True,autoincrement=True)
    prop_id =               Column("prop_id",Integer,ForeignKey('property.prop_id'))
    name =                  Column("name",Text,default='none')
    amount =                Column("amount",Numeric(10,2),default=0)
    user_id =               Column(Integer,ForeignKey('users.user_id'))