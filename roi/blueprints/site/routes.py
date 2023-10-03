from flask import Blueprint, render_template, request, flash, redirect,url_for
from flask_login import current_user, login_required
from sqlalchemy import select,text
from sqlalchemy import delete # type: ignore


from models import Property,Users,Income,Expenses,Product,db
from forms import AddImageForm,AddPropertyForm,ExpenseForm,IncomeForm,ProductForm
from helpers import calc_roi,get_image

site = Blueprint('site', __name__, template_folder='site_templates')


@site.route('/', methods = ['POST','GET'])
def index():
    return render_template('index.html')


@site.route('/account', methods = ['POST','GET'])
@login_required
def account():
    return render_template('my_account.html')

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
        purchase_price = form.purch_price.data
        new_property=Property(address=address,purch_price=purchase,est_rent=est_rent,_user_id=current_user.user_id)
        db.session.add(new_property)
        db.session.commit()
        prop_id_q = db.session.execute(select(Property.prop_id).where(Property.address == address))
        prop_id = prop_id_q.all()[0][0]
        expense_amount = purchase_price
        expense_name = "Purchase Price"
        new_expense=Expenses(name=expense_name,amount=expense_amount,prop_id=prop_id,user_id=current_user.user_id)
        db.session.add(new_expense)
        db.session.commit()

        prop = db.session.execute(select(Property).where(Property.prop_id==prop_id))
        exp_total = db.session.execute(text(f"select sum(amount) from expense inner join property on property.prop_id = expense.prop_id where expense.user_id = '{current_user.user_id}'"))
        inc_total = db.session.execute(text(f"select sum(amount) from income inner join property on property.prop_id = income.prop_id where income.user_id = '{current_user.user_id}'"))
        roi= calc_roi(prop.all()[0][0].purch_price,exp_total.all()[0][0],inc_total.all()[0][0])
        roif = "%.2f" % roi
        query=text(f'UPDATE property SET roi = {roif} WHERE property.prop_id = {prop_id}')
        db.session.execute(query)
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
    return render_template('add_image.html',form=form,prop_id=prop_id,property=property)

@site.route('/delete/<id>', methods=['POST','GET'])
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


##############################    STORE STUFF   #############################

@site.route('/store')
def store():

    store = Product.query.all()

    return render_template('store.html', store=store) 


@site.route('/store/create', methods = ['GET', 'POST'])
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
        print('fuck you i\'m in')
        print(description)
        print(name)
        print(image)
        print(price)
        print(quantity)

    #try: 
        this_product.name = name
        this_product.description = description
        if image:    
            this_product.image = image
        else:
            this_product.image = get_image(name)
        this_product.price = price
        this_product.quantity = quantity 

        

        db.session.commit()

        flash(f"You have successfully updated product {this_product.name}", category='success')
        return redirect('/store')

    #except:
        # flash("We were unable to process your request. Please try again ", category='warning')
        # return redirect('/store')
        
    return render_template('update_product.html', form=updateform, product=product)


@site.route('/store/delete/<id>')
def delete(id):

    product = Product.query.get(id)

    db.session.delete(product)
    db.session.commit()

    return redirect('/store')



