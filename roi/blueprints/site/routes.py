from flask import Blueprint, render_template, request, flash, redirect,url_for
from flask_login import login_required,current_user
from sqlalchemy import select

from roi.models import db,Property,Users,Income,Expenses
from roi.forms import AddImageForm,AddPropertyForm,ExpenseForm,IncomeForm








site = Blueprint('site', __name__, template_folder='site_templates')


@site.route('/', methods = ['POST','GET'])
def index():
    return render_template('index.html')

@site.route('/signup', methods = ['POST','GET'])
def sign_up():
    pass

@site.route('/account', methods = ['POST','GET'])
@login_required
def account():
    return render_template('my_account.html')

@site.route('/properties', methods = ['POST','GET'])
@login_required
def properties():
    prop_data=db.session.execute(select(Property).where(Users.user_id==current_user.user_id))
    print(current_user.user_id)
    if len(prop_data.all()) == 0:
        no_properties=True
        return render_template('my_properties.html', no_properties=no_properties)
    else:
        property_data = db.session.execute(select(Property).where(Users.user_id==current_user.user_id))
        properties=(property_data.freeze().data)
        income_data = db.session.execute(select(Income).where(Users.user_id==current_user.user_id))
            
        return render_template('my_properties.html',properties=properties)


@site.route('/add-edit',methods=['POST','GET'])
@login_required
def add_edit():
    form = AddPropertyForm()

    if form.validate_on_submit():
        address = form.address.data
        purchase = form.purch_price.data
        est_rent = form.est_rent.data

        new_property=Property(address=address,purch_price=purchase,est_rent=est_rent,user_id=current_user.user_id)
        db.session.add(new_property)
        db.session.commit()
        return redirect(url_for('properties'))

    return render_template('add_edit_property.html',form=form)


@site.route('/view-exp-inc',defaults={'id':0}, methods = ['POST','GET'])
@site.route('/view-exp-inc/<id>', methods = ['POST','GET'])
@login_required
def view_exp_inc(id):
    prop_data=db.session.execute(select(Property).where(Users.user_id==current_user.user_id))
    address = prop_data.freeze().data[0].address
    income_data = db.session.execute(select(Income).join(Property).filter(Income.prop_id == id))
    expense_data = db.session.execute(select(Expenses).join(Property).filter(Expenses.prop_id == id))
    incomes=(income_data.freeze().data)
    expenses=(expense_data.freeze().data)
    if len(incomes) < 1 and len(expenses) < 1:
        no_monies=True
        return render_template('inc_exp_view.html', no_monies=no_monies,address=address)
    else:
        income_sum=0
        for income in incomes:
            income_sum+=income.amount
            
        expense_sum=0
        for expense in expenses:
            expense_sum+=expense.amount
        

        return render_template('inc_exp_view.html',incomes=incomes,expenses=expenses,address=address,expense_sum=expense_sum,income_sum=income_sum)



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
    
@site.route('/contact', methods = ['POST','GET'])
def contact():
    return render_template('contact.html')