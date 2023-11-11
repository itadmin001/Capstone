from flask import Blueprint, render_template, request, flash, redirect,url_for,session,jsonify
from flask_login import current_user, login_required
from sqlalchemy import select,text
from sqlalchemy import delete # type: ignore


from models import Property,Users,Income,Expenses,Product,db
from forms import AddImageForm,AddPropertyForm,ExpenseForm,IncomeForm,ProductForm,UserAccountForm
from helpers import calc_roi,get_image,array_merge

site = Blueprint('site', __name__, template_folder='site_templates')


@site.route('/', methods = ['POST','GET'])
def index():
    return render_template('index.html')


@site.route('/account', methods = ['POST','GET'])
@login_required
def account():
    user = select(Users).where(Users.user_id == current_user.user_id)
    _user = db.session.execute(user)
    this_user = _user.all()[0][0]
    return render_template('my_account.html',user = this_user)

@site.route('/edit-account/<uid>', methods=['POST','GET'])
@login_required
def edit_account(uid):

    user = select(Users).where(Users.user_id == current_user.user_id)
    _user = db.session.execute(user)
    this_user = _user.all()[0][0]
    print(this_user.username)
    username = this_user.username
    fname = this_user.first_name
    lname = this_user.last_name
    address = this_user.address
    city = this_user.city
    state = this_user.state
    zip = this_user.zip
    about_me = this_user.about_me
    email = this_user.email
    phone = this_user.phone
    update_account = UserAccountForm(username=username,
                                     first_name=fname,
                                     last_name=lname,
                                     address=address,
                                     city=city,
                                     state=state,
                                     zip=zip,
                                     phone=phone,
                                     email=email,
                                     about_me=about_me
                                     )
    
    if request.method == 'POST' and update_account.validate_on_submit():
        username = update_account.username.data
        fname = update_account.first_name.data
        lname = update_account.last_name.data
        address = update_account.address.data
        city = update_account.city.data
        state = update_account.state.data
        zip = update_account.zip.data
        email = update_account.email.data
        phone = update_account.phone.data
        about_me = update_account.about_me_body.data

        this_user.username = username
        this_user.first_name = fname
        this_user.last_name = lname
        this_user.address = address
        this_user.city = city
        this_user.state = state
        this_user.zip = zip
        this_user.email = email
        this_user.phone = phone
        this_user.about_me = about_me

        db.session.commit()

        flash(f"User information udated!", category='success')
        return redirect('/account')

    return render_template('edit_account_details.html',form=update_account,user_id = current_user.user_id)

@site.route('/properties', methods = ['POST','GET'])
@login_required
def properties():
    
    prop_data= db.session.execute(text(f"SELECT * FROM property WHERE _user_id = '{current_user.user_id}'"))
    prop_count = len(prop_data.all())
    if prop_count < 1:
        return render_template('my_properties.html', no_properties=True)
    
    prop_data= db.session.execute(text(f"SELECT * FROM property WHERE _user_id = '{current_user.user_id}'"))
    properties = prop_data.all()


    return render_template('my_properties.html',properties=properties)


@site.route('/add-edit',methods=['POST','GET'])
@login_required
def add_edit():
    form = AddPropertyForm()  
    if form.validate_on_submit():
        address = form.address.data
        purchase = form.purch_price.data
        est_rent = form.est_rent.data

        new_property=Property(address=address,purch_price=purchase,est_rent=est_rent,_user_id=current_user.user_id)
        db.session.add(new_property)
        db.session.commit()
        return redirect(url_for('site.properties'))
    
    return render_template('add_edit_property.html',form=form)

@site.route('/Add-Image/<prop_id>',methods=['GET','POST'])
@login_required
def add_image(prop_id):
    form=AddImageForm()
    prop_data=db.session.execute(select(Property).join(Users).filter(Users.user_id==current_user.user_id).filter(Property.prop_id==prop_id))
    property = [data[0] for data in prop_data]
    if form.validate_on_submit():
        img_url = form.imageURL.data
        #### This looks like the safer and more acceptable way to add/update ####
        _user_id = current_user.user_id
        query = text('UPDATE property SET image = :img_url WHERE property.prop_id = :prop_id AND property._user_id = :_user_id')
        db.session.execute(query, {"img_url": img_url, "prop_id": prop_id, "_user_id": current_user.user_id})
        db.session.commit()
        return redirect('/properties')
    
    return render_template('add_image.html',form=form,prop_id=prop_id,property=property)


@site.route('/delete-property/<id>', methods=['POST','GET'])
@login_required
def prop_delete(id):
    query = f'DELETE FROM Property WHERE Property.prop_id = {id}'
    db.session.execute(text(query))
    db.session.commit()
    return redirect('/properties')


@site.route('/view-exp-inc',defaults={'id':0}, methods = ['POST','GET'])
@site.route('/view-exp-inc/<id>', methods = ['POST','GET'])
@login_required
def view_exp_inc(id):
    prop_data=db.session.execute(select(Property).join(Users).filter(Users.user_id==current_user.user_id).filter(Property.prop_id==id))
    property = [data[0] for data in prop_data]
    income_data = db.session.execute(select(Income).join(Property).filter(Income.prop_id == id))
    expense_data = db.session.execute(select(Expenses).join(Property).filter(Expenses.prop_id == id))
    incomes=(income_data.freeze().data)
    expenses=(expense_data.freeze().data)
    if len(incomes) < 1 and len(expenses) < 1:
        no_monies=True
        return render_template('inc_exp_view.html', no_monies=no_monies,property=property,id=id)
    else:
        income_sum=0
        for income in incomes:
            income_sum+=income.amount      
        expense_sum=0
        for expense in expenses:
            expense_sum+=expense.amount

        return render_template('inc_exp_view.html',incomes=incomes,expenses=expenses,property=property,expense_sum=expense_sum,income_sum=income_sum,id=id)


@site.get('/Income?prop_id=<id>')
def get_prop_id(id):
    return id
@site.route('/Income',defaults={'id':0},methods=['POST','GET'])
@site.route('/Income/<id>',methods=['POST','GET'])
@login_required
def add_inc(id):
    prop = db.session.execute(select(Property).where(Property.prop_id==id))
    address = prop.freeze().data[0].address
    form = IncomeForm()
    if request.method=="POST" and form.validate_on_submit():
        prop_id = id
        income_amount = form.income_amt.data
        income_name = form.income_name.data
       
        new_income=Income(name=income_name,amount=income_amount,prop_id=id,user_id=current_user.user_id)
        db.session.add(new_income)
        db.session.commit()
    
        prop = db.session.execute(select(Property).where(Property.prop_id==id))
        exp_total = db.session.execute(text(f"select sum(amount) from expense inner join property on property.prop_id = expense.prop_id where expense.user_id = '{current_user.user_id}'"))
        inc_total = db.session.execute(text(f"select sum(amount) from income inner join property on property.prop_id = income.prop_id where income.user_id = '{current_user.user_id}'"))
        roi= calc_roi(prop.all()[0][0].purch_price,exp_total.all()[0][0],inc_total.all()[0][0])
        roif = "%.2f" % roi
        query=text(f'UPDATE property SET roi = {roif} WHERE property.prop_id = {prop_id}')
        db.session.execute(query)
        db.session.commit()
        return redirect('/properties')
    
    
    return render_template('add_income.html',form=form,id=id,address=address)

@site.route('/Expense',defaults={'id':0},methods=['POST','GET'])
@site.route('/Expense/<id>',methods=['POST','GET'])
@login_required
def add_exp(id):
    prop = db.session.execute(select(Property).where(Property.prop_id==id))
    address = prop.freeze().data[0].address
    form = ExpenseForm()
    if request.method=="POST" and form.validate_on_submit():
        print("POST")
        prop_id = id
        expense_amount = form.expense_amt.data
        expense_name = form.expense_name.data
        print(f"Expense Amt: {expense_amount}\nExpense Name: {expense_name}\nProperty ID: {prop_id}")
        new_expense=Expenses(name=expense_name,amount=expense_amount,prop_id=id,user_id=current_user.user_id)
        db.session.add(new_expense)
        db.session.commit()
        return redirect('/properties')
    return render_template('add_expense.html',form=form,id=id,address=address)

@site.route('/delete-expense/<inc_id>&<id>',methods=['GET','POST'])
@login_required
def del_exp(inc_id,id):
    prop = db.session.execute(select(Property).where(Property.prop_id==id))
    db.session.execute(text(f'DELETE FROM expense WHERE expense.inc_id = {inc_id}'))
    db.session.commit()

    exp_total = db.session.execute(text(f'select sum(amount) from expense inner join property on property.prop_id = expense.prop_id where expense.user_id = {current_user.user_id}'))
    inc_total = db.session.execute(text(f'select sum(amount) from income inner join property on property.prop_id = income.prop_id where income.user_id = {current_user.user_id}'))
    
    if exp_total.all()[0][0] == None or inc_total.all()[0][0] == None:
        return redirect('/properties')
    
    roi= calc_roi(prop.all()[0][0].purch_price,exp_total.all()[0][0],inc_total.all()[0][0])
    roif = "%.2f" % roi
    query=text(f'UPDATE property SET roi = {roif} WHERE property.prop_id = {id}')
    db.session.execute(query)
    db.session.commit()
    return redirect('/properties')

@site.route('/delete-income/<inc_id>&<id>',methods=['GET','POST'])
@login_required
def del_inc(inc_id,id):
    prop = db.session.execute(select(Property).where(Property.prop_id==id))
    db.session.execute(text(f'DELETE FROM income WHERE income.inc_id = {inc_id}'))
    db.session.commit()

    exp_total = db.session.execute(text(f"select sum(amount) from expense inner join property on property.prop_id = expense.prop_id where expense.user_id = '{current_user.user_id}'"))
    inc_total = db.session.execute(text(f"select sum(amount) from income inner join property on property.prop_id = income.prop_id where income.user_id = '{current_user.user_id}'"))
    
    # if exp_total.all()[0][0] == None or inc_total.all()[0][0] == None:
    #     return redirect('/properties')
    
    roi= calc_roi(prop.all()[0][0].purch_price,exp_total.all()[0][0],inc_total.all()[0][0])
    roif = "%.2f" % roi
    query=text(f'UPDATE property SET roi = {roif} WHERE property.prop_id = {id}')
    db.session.execute(query)
    db.session.commit()
    return redirect('/properties')
    
@site.route('/contact', methods = ['POST','GET'])
def contact():
    return render_template('contact.html')


##############################    STORE FUNCTIONS   #############################

@site.route('/store')
@login_required
def store():

    store = Product.query.all()

    return render_template('store.html', store=store) 


@site.route('/store/create', methods = ['GET', 'POST'])
@login_required
def create():

    addProductForm = ProductForm()

    if request.method == 'POST' and addProductForm.validate_on_submit():

        name = addProductForm.name.data
        desc = addProductForm.description.data
        image = addProductForm.image.data
        price = addProductForm.price.data
        quantity = addProductForm.quantity.data 

        newProduct = Product(name, price, quantity, image, desc)

        db.session.add(newProduct)
        db.session.commit()

        flash(f"You have successfully created product {name}", category='success')
        return redirect('/store')

    return render_template('create.html', form=addProductForm)


@site.route('/store/update/<id>', methods = ['GET', 'POST'])
@login_required
def update(id):
    prod = select(Product).where(Product.prod_id == id)
    product = db.session.execute(prod)
    this_product = product.all()[0][0]
    description = this_product.description
    name = this_product.name
    image = this_product.image
    price = this_product.price
    quantity = this_product.quantity
    updateform = ProductForm(name=name,description=description,image=image,price=price,quantity=quantity)
    

    if request.method == 'POST' and updateform.validate_on_submit():
        description = updateform.description.data
        name = updateform.name.data
        image = updateform.image.data
        price = updateform.price.data
        quantity = updateform.quantity.data

        this_product.name = name
        this_product.description = description
        if image:    
            this_product.image = image
        else:
            this_product.image = get_image(name)
        this_product.price = price
        this_product.quantity = quantity 

        

        db.session.commit()

        flash(f"Updated product {this_product.name}", category='success')
        return redirect('/store')

        
    return render_template('update_product.html', form=updateform, product=product)


@site.route('/store/delete-product-store/<id>')
@login_required
def delete(id):

    product = Product.query.get(id)

    db.session.delete(product.prod_id)
    db.session.commit()

    return redirect('/store')


@site.route('/store/add-to-cart/<prod_id>', methods=['POST', 'GET'])
@login_required
def add_to_cart(prod_id):
    # try:
    product_id = prod_id
    product = Product.query.filter_by(prod_id=product_id).first()

    cart_total = 0
    cart_total_item_count = 0

    session.modified = True
    if 'cart_item' in session:
        print('cart not empty')
        if product_id in session['cart_item'].keys():
            print("item exists in cart")
            quantity = session['cart_item'][product_id]['quantity'] + 1
            print(f"CART TOTAL: {session['cart_total']}")
            cart_total = session['cart_total'] + session['cart_item'][product_id]['price']
            

        else:
            print("merging")
            itemArray = { product.prod_id : {'name' : product.name, 'prod_id' : product.prod_id, 'quantity' : 1, 'price' : product.price, 'image' : product.image, 'item_total': product.price}}
            session['cart_item'] = array_merge(session['cart_item'], itemArray)
        
        for key, value in session['cart_item'].items():
            individual_quantity = int(session['cart_item'][key]['quantity'])
            individual_price = float(session['cart_item'][key]['price'])
            cart_total_item_count = cart_total_item_count + individual_quantity
            cart_total = float(cart_total) + individual_price
    else:
        quantity = 1
        itemArray = { product.prod_id : {'name' : product.name, 'prod_id' : product.prod_id, 'quantity' : quantity, 'price' : product.price, 'image' : product.image, 'item_total': quantity * product.price}}
        session['cart_item'] = itemArray
        cart_total_item_count = cart_total_item_count + quantity
        cart_total = cart_total + quantity * product.price
        
    session['cart_total_item_count'] = cart_total_item_count
    session['cart_total'] = cart_total
    return redirect('/store')

    # except Exception as e:
    #     print("Exception")
    #     print(e)
    # finally:
    #     print('fell thru to finally')
        # return redirect('/store')


@site.route('/store/cart', methods=['POST','GET'])
@login_required
def cart():
    print(f"CART SESSION: {session}")
    return render_template('cart.html', session = session)

@site.route('/store/empty',methods=['POST','GET'])
@login_required
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('site.store'))
    except Exception as e:
        print(e)
    return redirect(url_for('site.store'))


@site.route('/store/delete-product-cart/<string:prod_id>', methods=['POST','GET'])
@login_required
def delete_product_cart(prod_id):
    cart_total = 0
    cart_total_item_count = 0
    session.modified=True
    for cart_item in session['cart_item'].items():
        if cart_item[0] == prod_id:
            session['cart_item'].pop(cart_item[0],None)
            if 'cart_item' in session:
                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['price'])
                    cart_total_item_count = cart_total_item_count + individual_quantity
                    cart_total =cart_total + individual_price
            break
    if cart_total_item_count == 0:
        session.clear()
        return redirect('/store/empty')
    else:
        session['cart_total'] = cart_total
            
    return redirect(url_for('site.cart'))


@site.route('/store/item-detail/<string:prod_id>', methods=['POST','GET']) #type: ignore
@login_required
def item_detail(prod_id):
    product = Product.query.filter_by(prod_id=prod_id).first()

    return render_template('shop_item_detail.html',product=product)

@site.route('/update_session', methods=['POST','GET'])
@login_required
def update_session():
    keys=[]
    extractedKeys =[]
    data = request.json
    i = 0
    for key, item in data.items():
       for k in range(len(item)):
           print(item[k])
           keys.append(item[k].keys())
    for key in keys:
        product_id = list(key)[0]
        session['cart_item'][product_id]['quantity'] = data[product_id]['quantity']
        session['cart_item'][product_id]['item_total'] = data[product_id]['item_total']
    
        ct = data['cart_total']
        cart_total = "%.2f" % float(ct)
        print(f"CART TTL: {cart_total}")
        session['cart_total'] = cart_total
        session.modified=True
    flash("Cart Updated!",category='success')
    return jsonify(success=True)