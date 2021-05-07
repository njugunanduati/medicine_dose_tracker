from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForm, DrugForm, DrugCategoryForm, DosageForm, RegistrationForm, ResetPasswordForm, \
    ResetPasswordRequestForm
from app.models import User, Drug, DrugCategory, Dosage


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('auth/register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def index():
    drugs = Drug.query.all()
    dosages = Dosage.query.all()
    return render_template('dashboard.html', title='Home', drugs=drugs,  dosages=dosages)


@app.route('/drug/category')
@login_required
def get_drug_categories():
    drug_categories = DrugCategory.query.all()
    return render_template('book_types.html', title='DrugCategory', drug_categories=drug_categories)


@app.route('/add/drug/category', methods=['GET', 'POST'])
@login_required
def add_drug_category():
    form = DrugCategoryForm()
    if form.validate_on_submit():
        drug_category = DrugCategory(
            name=form.name.data,
        )
        db.session.add(drug_category)
        db.session.commit()
        return redirect(url_for('get_book_types'))
    return render_template('add_book_type.html', title='Add Book', form=form)
