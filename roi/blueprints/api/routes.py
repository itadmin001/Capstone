
from flask import Blueprint, request, jsonify 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import text

from models import Users, Product, ProdOrder, Order, Customer, db, products_schema, product_schema

api = Blueprint('api', __name__, url_prefix = '/api') #all of our endpoints need to be prefixed with /api


@api.route('/token', methods = ['GET', 'POST'])
def token():

    data = request.json

    if data:
        client_id = data['client_id']
        access_token = create_access_token(identity=client_id) 
        return {
            'status' : 200,
            'access_token' : access_token 
        }
    
    else:
        return {
            'status': 400,
            'message': 'Missing Client Id. Try Again'
        }
    

@api.route('/store')
@jwt_required()
def get_store():
    store=Product.query.all()

    response=products_schema.dump(store)
    return jsonify(response)


@api.route('/order/<cust_id>')
@jwt_required()
def get_order(cust_id):

    prodorder = ProdOrder.query.filter(ProdOrder.cust_id == cust_id).all()

    data=[]

    for order in prodorder:
        product=Product.query.filter(Product.prod_id == order.prod_id).first()

        prod_data = product_schema.dump(product)

        prod_data['quantity'] = order.quantity
        prod_data['order_id'] = order.order_id 
        prod_data['id'] = order.prod_id 

        data.append(prod_data)
    return jsonify(data)


@api.route('/order/create/<cust_id>', methods=['POST','PUT','GET'])
@jwt_required()
def create_order(cust_id):
    print(f"cust_id {cust_id}")
    data = request.json

    customer_order=data['order']

    customer = Customer.query.filter(Customer.cust_id == cust_id).first()
    if not customer:
        print("NOT CUSTOMER")
        customer = Customer(cust_id)
        db.session.add(customer)

    order = Order()
    db.session.add(order)
    print(f"ORDER ID: {order.order_id}")
    for product in customer_order:
        
        query = f'INSERT INTO \"productOrder\" (prodorder_id, prod_id, quantity, price, order_id, cust_id) VALUES (\'{order.order_id}\',\'{product["prod_id"]}\', {product["quantity"]}, {product["price"]},\'{order.order_id}\',\'{cust_id}\') '
        prodorder = db.session.execute(text(query))
        db.session.add(prodorder)

        order.increment_order_total(product.price)

        current_product = Product.query.filter(Product.prod_id == product['prod_id']).first()
        current_product.decrement_quantity(product['quantity'])
        
    db.session.commit()
    return {
        'status':200,
        'message':'A new order was created'
    }


@api.route('/order/update/<order_id>',methods=['PUT','POST'])
@jwt_required()
def update_order(order_id):

    data=request.json
    new_quantity = int(data['quantity'])
    prod_id = data['prod_id']
    print(prod_id)
    prodorder = ProdOrder.query.filter(ProdOrder.order_id ==order_id,ProdOrder.prod_id==prod_id).first()
    order = Order.query.get(order_id)
    product = Product.query.get(prod_id)
    prodorder.set_price(product.price,new_quantity)

    diff = abs(prodorder.quantity - new_quantity)

    if prodorder.quantity < new_quantity:
        product.decrement_quantity(diff)
        order.increment_order_total(prodorder.price)

    elif prodorder.quantity > new_quantity:
        product.increment_quantity(diff)
        order.decrement_order_total(prodorder.price)


    prodorder.update_quantity(new_quantity)

    db.session.commit()

    return {

        'status':200,
        'message':"Order was successfully updated"
    }


@api.route('/order/delete/<order_id>',methods=['DELETE'])
@jwt_required()
def delete_item_order(order_id):
    
    data = request.json
    prod_id = data['prod_id']
    
    prodorder = ProdOrder.query.filter(ProdOrder.order_id == order_id, ProdOrder.prod_id == prod_id).first()

    order= Order.query.get(order_id)
    product = Product.query.get(prod_id)

    order.decrement_order_total(prodorder.price)
    product.increment_quantity(prodorder.quantity)

    db.session.delete(prodorder)
    db.session.commit()

    return{
        'status':200,
        'message':"Order Delete Success"
    }