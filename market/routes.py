from market import app, db
from flask import render_template
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm
from flask import redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/market', methods=['GET','POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    if request.method == "POST":
        purchase_item = request.form.get('purchased_item')
        purchase_item_object = Item.query.filter_by(name = purchase_item).first()
        if purchase_item_object:
            if current_user.can_purchase(purchase_item_object):
                purchase_item_object.buy(current_user)
                flash(f"Item { purchase_item_object.name } purchased for { purchase_item_object.price }", category='success')
            else:
                flash(f"You're too broke to buy this", category='danger')

        return redirect(url_for('market_page'))
    
    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        return render_template('market.html', items=items, purchase_from=purchase_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created, you are now logged in as {{ user_to_create.username }}", category="success")
        return redirect(url_for('market_page')) 
    
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')  
        
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and Password do not match, try again', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for('index.html'))