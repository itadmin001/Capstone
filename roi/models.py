from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer,DateTime,ForeignKey,Text,text,Numeric
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from datetime import datetime
import uuid
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash

# Internal
from helpers import get_image

db=SQLAlchemy()
ma = Marshmallow()



class Users(db.Model,UserMixin):
    __tablename__ = "users"
    user_id =           Column("user_id", String ,primary_key=True)
    first_name =        Column("fname",Text,default="none")
    last_name =         Column("lname",Text,default="none")
    email =             Column("email",Text,unique=True,nullable=False)
    phone =             Column("phone",Text,default="none")
    username =          Column("username",Text,unique=True,nullable=False)
    password =          Column("pwd",Text,nullable=False)
    created_on =        Column("created_on", DateTime(timezone=True),default=datetime.now())

    def __init__(self,username,email,password,first_name="",last_name="",phone = ""):
        self.user_id = self.set_id()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.password = password
        self.username = username

    def pass_hash(password):
        hash_pwd = generate_password_hash(password)
        return hash_pwd
    
    def set_id(self):
        return str(uuid.uuid4())
    
    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"User: {self.first_name} {self.last_name} Email: {self.email}"
    
class Customer(db.Model):
    __tablename__ =         "customer"
    cust_id =               Column(String, primary_key=True)
    date_created =          Column(DateTime,default=datetime.utcnow())
    product_order =         relationship('ProdOrder', backref='customer',lazy=True)

    def __init__(self,cust_id):
        self.cust_id = cust_id


class Income(db.Model):
    __tablename__ =         "income"
    inc_id =                Column("inc_id",Integer, primary_key=True,autoincrement=True)
    prop_id =               Column("prop_id",Integer,ForeignKey('property.prop_id',ondelete='cascade'))
    name =                  Column("name",Text,default = "")
    amount =                Column("amount",Numeric(10,2),default=0)
    user_id =               Column(String,ForeignKey('users.user_id'))

    def __init__(self,prop_id,name,amount,user_id):
        self.prop_id = prop_id
        self.name = name
        self.amount = amount
        self.user_id = user_id

    def __repr__(self):
        return f"<INCOME: {self.name} AMOUNT: {self.amount}>"
    
class Expenses(db.Model):
    __tablename__ =         "expense"
    exp_id =                Column("inc_id",Integer, primary_key=True,autoincrement=True)
    prop_id =               Column("prop_id",Integer,ForeignKey('property.prop_id',ondelete='cascade'))
    name =                  Column("name",Text,default='none')
    amount =                Column("amount",Numeric(10,2),default=0)
    user_id =               Column(String,ForeignKey('users.user_id'))

    def __init__(self,prop_id,name,amount,user_id):
        self.prop_id = prop_id
        self.name =  name
        self.amount = amount
        self.user_id = user_id

    def __repr__(self):
        return f"<EXPENSE: {self.name} AMOUNT: {self.amount}>"

class Property(db.Model):
    __tablename__ =         "property"
    prop_id =               Column(Integer, primary_key=True,autoincrement=True)
    address =               Column(Text,nullable=False)
    purch_price =           Column(Numeric(10,2),nullable=False)
    est_rent =              Column(Numeric(10,2),nullable=False)
    _user_id =              Column(String(50),ForeignKey('users.user_id',ondelete='cascade'))
    image =                 Column(String, nullable=False)
    roi =                   Column(Numeric(5,2))
    income =                relationship('Income', backref='property', cascade='all,delete',passive_deletes=True)
    expenses =              relationship('Expenses', backref='property', cascade='all,delete',passive_deletes=True)
    
    def __init__(self,address,purch_price,est_rent,_user_id,image=""):
        self.address = address
        self.purch_price = purch_price
        self.est_rent = est_rent
        self._user_id = _user_id
        self.image = self.set_image(image,address)

    def set_image(self,image,address):
        if not image:
            image=get_image(address)
        return image
    
    def __repr__(self):
        return f"<ADDRESS: {self.address} PROPERTY: {self.prop_id}>"
    

class Product(db.Model):
    __tablename__ = "product"
    prod_id =       Column(String, primary_key = True)
    name =          Column(String(100), nullable = False)
    image =         Column(String, nullable = False)
    description =   Column(String(1500))
    price =         Column(Numeric(precision=10, scale=2), nullable = False)
    quantity =      Column(Integer, nullable = False)
    date_added =    Column(DateTime, default = datetime.utcnow)
    prodorder =     relationship('ProdOrder', backref = 'product', lazy=True)
    
    def __init__(self,name,price,quantity,image = "",description = ""):
        self.prod_id = self.set_id()
        self.name = name
        self.price = price
        self.quantity = quantity
        self.image = self.set_image(image,name)
        self.description = description

    def set_id(self):
        return str(uuid.uuid4())
    

    def set_image(self, image, name):
        if not image:
            image = get_image(name)

        return image
    
    def decrement_quantity(self,quantity):
        self.quantity -= int(quantity)
        return self.quantity
    
    def increment_quantity(self, quantity):
        self.quantity += int(quantity)


class ProdOrder(db.Model):
    __tablename__ =     "productOrder"
    prodorder_id =      Column(String, primary_key = True)
    prod_id =           Column(String, ForeignKey('product.prod_id'), nullable = False)
    quantity =          Column(Integer, nullable = False)
    price =             Column(Numeric(precision = 10, scale = 2), nullable = False)
    order_id =          Column(String,  ForeignKey('order.order_id'), nullable = False)
    cust_id =           Column(String, ForeignKey('customer.cust_id'), nullable=False)


    def __init__(self,prod_id,quantity,price,order_id,user_id):
        self.prodorder_id = self.set_id()
        self.prod_id = prod_id
        self.quantity = quantity
        self.price = self.set_price(price,quantity)
        self.order_id = order_id
        self.user_id = user_id 


    def set_id(self):
        return str(uuid.uuid4())
    


    def set_price(self,price,quantity):

        quantity = int(quantity)
        price = float(price)

        self.price = quantity * price
        return self.price 
    

    def update_quantity(self,quantity):

        self.quantity = int(quantity)
        return self.quantity
    

class Order(db.Model):
    __tablename__ =  'order'
    order_id =      Column(String, primary_key = True)
    order_total =   Column(Numeric(precision = 10, scale = 2), nullable = False)
    date_created =  Column(DateTime, default = datetime.utcnow())
    prodorder =     relationship('ProdOrder', backref = 'order', lazy = True)


    def __init__(self):
        self.order_id = self.set_id()
        self.order_total = 0.00


    def set_id(self):
        return str(uuid.uuid4())
    
    def increment_order_total(self,price):

        self.order_total = self.order_total
        self.order_total += price

        return self.order_total
    
    def decrement_order_total(self,price):

        self.order_total = self.order_total
        self.order_total -= price


        return self.order_total 
    
    def __repr__(self):

        return f"<ORDER: {self.order_id}>"
    

class ProductSchema(ma.Schema):
    class Meta: 
        fields = ['prod_id', 'name', 'image', 'description', 'price', 'quantity'] 


product_schema = ProductSchema()
products_schema = ProductSchema(many = True)