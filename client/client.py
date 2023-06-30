import os
from webapp import app,db
from models import User,Model,Image
import webapp.auth.email,webapp.auth.forms,webapp.auth.routes,webapp.main.forms,webapp.errors.handlers,webapp.main.routes
from flask import Flask,flash, request,render_template,redirect,url_for,get_flashed_messages
from werkzeug.utils import secure_filename
from flask_login import login_required
app.config["DEBUG"] = True
# app.config['UPLOAD_FOLDER'] = 'client/UploadFolder/'
UPLOAD_FOLDER='./UploadFolder/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'h5'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
cwd = os.getcwd()
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Model': Model, 'Image': Image}

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def uploadfile():
      return render_template('upload.html')

@app.route('/uploader', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method =='POST':
        files = request.files.getlist("file[]")
        # print(request.files)
        for file in files:
            path = os.path.dirname(file.filename)
            path2 = os.path.join(app.config['UPLOAD_FOLDER'], path)
            path3 = os.path.join(path2, path)
            if not os.path.exists(path2):
                os.makedirs(path2)
            
            filename = os.path.join(path, secure_filename(os.path.basename(file.filename)))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Upload success!')
        return redirect(url_for('index'))
    # return redirect(url_for('uploadfile'))

if __name__ == '__main__':
	app.run(host='localhost', port=8001, debug=True, use_reloader=True)
