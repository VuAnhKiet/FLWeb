from flask import Flask,flash, request,render_template,redirect,url_for,get_flashed_messages
import requests, json
import ast
import os
from fl_agg import model_aggregation
from werkzeug.utils import secure_filename
from form import LoginForm,EditProfileForm,ResetPasswordRequestForm
from app import app,db
from models import User,Model,Image
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.forms import RegistrationForm,ResetPasswordForm
from datetime import datetime
from app.email import send_password_reset_email
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from model_train import train
import cv2
import ast
import numpy as np
from werkzeug.urls import url_parse

app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = 'main_server/UploadFolder'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'h5'}
cwd = os.getcwd()
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Model': Model, 'Image': Image}

@app.route('/')
def hello():
	return render_template("index.html")
@app.route('/home')
def index():
	return render_template("index.html")

		
@app.route('/aggmodel', methods=['POST'])
def get_agg_model():
	if os.path.isdir(cwd + '/model_update') == False:
		os.mkdir(cwd + '/model_update')
	if request.method == 'POST':
		file = request.files['model'].read()
		fname = request.files['json'].read()

		fname = ast.literal_eval(fname.decode("utf-8"))
		fname = fname['fname']
		print(fname)

		wfile = open(cwd + "/model_update/"+fname, 'wb')
		wfile.write(file)
			
		return "Model received!"
	else:
		return "No file received!"
		
@app.route('/sendmodel')
@login_required
def send_model():
	api_url = 'http://localhost:8000/clientstatus'

	data = {'client_id': '8001'}
	print(data)

	r = requests.post(url=api_url, json=data)
	print(r, r.status_code, r.reason, r.text)
	if r.status_code == 200:
		print("OK")
		
	file = open(cwd + "/local_model/model1.h5", 'rb')
	data = {'fname':'model1.h5', 'id':'http://localhost:8001/'}
	files = {
		'json': ('json_data', json.dumps(data), 'application/json'),
		'model': ('model1.h5', file, 'application/octet-stream')
	}

	req = requests.post(url='http://localhost:8000/cmodel', 
						files=files)
	req1 = requests.post(url='http://localhost:8000/cfile', 
						files=files)

	# print(req.text)
	return render_template("index.html")
		

@app.route('/uploader', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      return 'file uploaded successfully'

@app.route('/upload')
@login_required
def uploadfile():
      return render_template('upload.html')

@app.route('/modeltrain')
@login_required
def model_train():
	if os.path.isdir(cwd + '/static') == False:
		os.mkdir(cwd + '/static')
	y,z = train()
	accuracy = y["accuracy"]
	loss = y["loss"]
	val_accuracy = y["val_accuracy"]
	val_loss = y["val_loss"]
	N = len(loss) 
	plt.style.use("ggplot")
	plt.figure()
	plt.plot(np.arange(0, N), loss, label="train_loss")
	plt.plot(np.arange(0, N), accuracy, label="train_acc")
	plt.plot(np.arange(0, N), val_loss,label="val_loss" )
	plt.plot(np.arange(0, N), val_accuracy, label="val_acc")
	plt.title("Training Loss and Accuracy for Federated Client 1")
	plt.xlabel("Epochs")
	plt.ylabel("Loss/Accuracy")
	plt.legend(loc="center right")
	plt.savefig(cwd + "/static/plot1.jpg")
	image = [i for i in os.listdir('static') if i.endswith('.jpg')][0]
	
	return render_template('train.html',epoch = len(loss),loss = loss ,accuracy = accuracy,val_loss = val_loss ,val_accuracy = val_accuracy, name = z, user_image = image)

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
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    model = [
        {'user': user, 'fname': 'Test #1'},
        {'user': user, 'fname': 'Test #2'}
    ]
    return render_template('user.html', user=user, model=model)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

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

if __name__ == '__main__':
	app.run(host='localhost', port=8001, debug=False, use_reloader=True)
