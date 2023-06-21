from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Length, Email
 
class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember_me = BooleanField('Ghi nhớ lần đăng nhập kế tiếp')
    submit = SubmitField('Đăng nhập')

class EditProfileForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    about_me = TextAreaField('Giới thiệu về bản thân', validators=[Length(min=0, max=140)])
    submit = SubmitField('Hoàn tất')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Yêu cầu cài lại mật khẩu')