from flask import Flask,flash, request,render_template,redirect,url_for
import requests, json
import ast
import os
from fl_agg import model_aggregation
from werkzeug.utils import secure_filename
from form import LoginForm,EditProfileForm,ResetPasswordRequestForm
from app import app,db,admin
from models import User,Model,Image
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.forms import RegistrationForm,ResetPasswordForm
from datetime import datetime
from app.email import send_password_reset_email
from flask_admin.contrib.sqla import ModelView



app.config['UPLOAD_FOLDER'] = 'main_server/UploadFolder'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
cwd = os.getcwd()
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Model': Model, 'Image': Image}

@app.route('/')
def server():
    users = User().query.all()
    return render_template("admin.html",users=users)

@app.route('/clientstatus', methods=['GET','POST'])
def client_status():
	url = "http://localhost:8001/serverack"

	if request.method == 'POST':
		client_port = request.json['client_id']
		
		with open(cwd + '/clients.txt', 'a+') as f:
			f.write('http://localhost:' + client_port + '/\n')

		print(client_port)

		if client_port:
			serverack = {'server_ack': '1'}
			return str(serverack)
		else:
			return "Client status not OK!"
	else:
		return "Client GET request received!"
		
@app.route('/cfile', methods=['POST'])
def filename():
	if request.method == 'POST':
		file = request.files['model'].read()
		fname = request.files['json'].read()
		# cli = request.files['id'].read()

		fname = ast.literal_eval(fname.decode("utf-8"))
		cli = fname['id']+'\n'
		fname = fname['fname']
		
		return "<h1>str(fname)</h1>"
		
@app.route('/cmodel', methods=['POST'])
def getmodel():
	if os.path.isdir(cwd + '/client_models') == False:
		os.mkdir(cwd + '/client_models')
	if request.method == 'POST':
		file = request.files['model'].read()
		fname = request.files['json'].read()
		# cli = request.files['id'].read()

		fname = ast.literal_eval(fname.decode("utf-8"))
		cli = fname['id']+'\n'
		fname = fname['fname']

		# with open('clients.txt', 'a+') as f:
		# 	f.write(cli)
		
		print(fname)
		wfile = open(cwd + "/client_models/"+fname, 'wb')
		wfile.write(file)
			
		return "Model received!"
	else:
		return "No file received!"
		
@app.route('/aggregate_models')
def perform_model_aggregation():
	model_aggregation()
	return render_template("agg.html")

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      return 'file uploaded successfully'

@app.route('/upload')
def uploadfile():
      return render_template('upload.html')

@app.route('/send_model_clients')
def send_agg_to_clients():
	clients = ''
	with open(cwd + '/clients.txt', 'r') as f:
		clients = f.read()
	clients = clients.split('\n')
	
	for c in clients:
		if c != '':
			file = open(cwd + "/agg_model/agg_model.h5", 'rb')
			data = {'fname':'agg_model.h5'}
			files = {
				'json': ('json_data', json.dumps(data), 'application/json'),
				'model': ('agg_model.h5', file, 'application/octet-stream')
			}
			
			print(c+'aggmodel')
			req = requests.post(url=c+'aggmodel', files=files)
			print(req.status_code)
	
	return render_template("sent.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('.index'))
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
	app.run(host='localhost', port=8000, debug=True, use_reloader=True)
