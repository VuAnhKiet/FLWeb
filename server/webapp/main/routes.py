from flask import Flask,flash, request,render_template,redirect,url_for,get_flashed_messages
import requests, json
import ast
import os
from fl_agg import model_aggregation
from werkzeug.utils import secure_filename
from webapp.main.forms import LoginForm,EditProfileForm,ResetPasswordRequestForm
from webapp import app,db
from models import User,Model,Image
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cv2
import ast
import numpy as np

cwd = os.getcwd()


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
	
@app.route('/')
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
			
		return "Nhận được mô hình"
	else:
		return "Không nhận được"
	
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
      file = request.files['file']
      upload = Model(filename=file.filename, model=file.read(), user_id=current_user.id)
      db.session.add(upload)
      db.session.commit()
    #   f.save(secure_filename(f.filename))
      return f'Upload success'

@app.route('/upload')
@login_required
def uploadfile():
      return render_template('upload.html')


