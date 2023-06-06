from flask import Flask,flash, request,render_template,redirect,url_for
import requests, json
import ast
import os
from fl_agg import model_aggregation
from werkzeug.utils import secure_filename
from form import LoginForm
from app import app,db
from models import User,Model,Image
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.forms import RegistrationForm

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
def hello():
	return render_template("index.html")
@app.route('/home')
def index():
	return render_template("index.html")

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

if __name__ == '__main__':
	app.run(host='localhost', port=8000, debug=False, use_reloader=True)
