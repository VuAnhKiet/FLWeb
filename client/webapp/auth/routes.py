import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from model_train import train
from webapp import app,db
import cv2
import ast
import os
import numpy as np
from werkzeug.urls import url_parse
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from webapp.main.forms import LoginForm,EditProfileForm,ResetPasswordRequestForm
from flask import Flask,flash, request,render_template,redirect,url_for
from models import User,Model,Image
from webapp.auth.forms import RegistrationForm,ResetPasswordForm
from webapp.email import send_password_reset_email
import shutil

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Tên đăng nhập hoặc mật khẩu không hợp lệ')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('auth/login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    # location="./UploadFolder/"
    # dir="image_dataset_path"
    # path=os.path.join(location,dir)
    # shutil.rmtree(path)
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Đăng ký thành công')
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
        flash('Vui lòng kiểm tra email của bạn và làm theo hướng dẫn')
        return redirect(url_for('login'))
    return render_template('auth/reset_password_request.html',
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
        flash('Mật khẩu của bạn đã được cài lại')
        return redirect(url_for('login'))
    return render_template('auth/reset_password.html', form=form)
