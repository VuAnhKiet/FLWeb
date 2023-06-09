from flask import Flask,flash, request,render_template,redirect,url_for,get_flashed_messages
import requests, json
import ast
import os
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
from model_train import train
import cv2
import ast
import numpy as np
from models import User
from flask import g

cwd = os.getcwd()

# UPLOAD_FOLDER='./client/'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'h5'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
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
            
        return "Đã nhận mô hình"
    else:
        return "Không tìm thấy"
    
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

# @app.route('/uploader', methods=['GET', 'POST'])
# @login_required
# def upload_file():
#     if request.method =='POST':
#         files = request.files.getlist("file[]")
#         print(request.files)
#         for file in files:
#             path = os.path.dirname(file.filename)
#             path2 = os.path.join(app.config['UPLOAD_FOLDER'], path)
#             if not os.path.exists(path2):
#                 os.mkdir(path2)
#             filename = os.path.join(path, secure_filename(os.path.basename(file.filename)))
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         return 'Files uploaded.'
#     # return redirect(url_for('uploadfile'))


# @app.route('/upload', methods=['GET', 'POST'])
# @login_required
# def uploadfile():
#       return render_template('upload.html')

@app.route('/modeltrain')
@login_required
def model_train():
    if os.path.isdir("../server" + '/static') == False:
        os.mkdir("../server" + '/static')
    if current_user.is_authenticated:
        g.user = current_user.get_id()
    g.user=str(g.user)
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
    plt.title("Training Loss and Accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Loss/Accuracy")
    plt.legend(loc="center right")
    plt.savefig("../server" + "/static/"+"plot_"+g.user+".jpg")
    # image = [i for i in os.listdir('static') if i.endswith('.jpg')][0]
    
    return render_template('train.html',epoch = len(loss),loss = loss ,accuracy = accuracy,val_loss = val_loss ,val_accuracy = val_accuracy, name = z)


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
        flash('Thay đổi của bạn đã được cập nhật!')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)