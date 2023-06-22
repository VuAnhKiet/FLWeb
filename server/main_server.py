from flask import Flask,flash, request,render_template,redirect,url_for
import requests, json
import ast
import os
from fl_agg import model_aggregation
from werkzeug.utils import secure_filename
from webapp.main.forms import LoginForm,EditProfileForm,ResetPasswordRequestForm
from webapp import app,db,admin
from models import User,Model,Image,UserRole
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from webapp.auth.forms import RegistrationForm,ResetPasswordForm
from datetime import datetime
from webapp.email import send_password_reset_email
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose,AdminIndexView,Admin
from models import User,Model,Image,UserRole
from flask_admin.contrib.fileadmin import FileAdmin
import hashlib
UPLOAD_FOLDER = "/Upload"
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'h5'}
cwd = os.getcwd()
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
path=os.path.join(os.path.dirname(__file__),'static')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Model': Model, 'Image': Image}

# @app.route('/')
# def server():
#     return render_template("admin/index.html")

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
            
        return "Nhận được mô hình"
    else:
        return "Không nhận được"
        
@app.route('/aggregate_models')
def perform_model_aggregation():
    model_aggregation()
    return redirect('/admin')

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files["file"]       
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(file.filename)
            return f'Files Uploaded !'

@app.route('/upload')
def uploadfile():
      return render_template('/upload.html')

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
    users=User.query
    return redirect('/admin')

def checklogin(username,password):
    if username and password:
        password= str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return User.query.filter(User.username.__eq__(username.strip()),User.password_hash.__eq__(password)).first()
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    username=request.form.get('username')
    password=request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return redirect(url_for('login'))
    login_user(user)
    return redirect('/admin')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# class MyHomeView(AdminIndexView):
#     @expose('/')
#     def index(self):
#         User=User
#         UserRole=UserRole
#         return self.render('admin/index.html',User=User,UserRole=UserRole )
    


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN
    
class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN
    
class AuthenticatedFileAdminlView(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN
class UploadView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        # Here are the contents of your "contact" route function
        return self.render('upload.html')
    

class AggModel(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        model_aggregation()
        return self.render('agg.html')
    

class SentModel(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        return self.render('sent.html')
    @expose('/send_model_clients')
    def send_model():
        users=User().query.filter_by(id=id).first()
        return render_template('templates/sent.html',users=users)
    



class Logout(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        logout_user()
        return self.render('admin/index.html')
    



admin.add_view(AuthenticatedModelView(User,db.session))
admin.add_view(UploadView('Tải lên', url='/upload'))
# admin.add_view(AggModel('AGGMODEL', url='/aggregate_models'))
# admin.add_view(SentModel('SENTMODEL', url='/send_model_clients'))
admin.add_view(AuthenticatedFileAdminlView(path, '/static/', name='Biểu đồ'))
admin.add_view(Logout('Đăng xuất'))







if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True, use_reloader=True)
