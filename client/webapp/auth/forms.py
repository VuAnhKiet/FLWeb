from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from models import User
 
 
class RegistrationForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    password2 = PasswordField(
        'Nhập lại mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')
 
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Xin hãy dùng tên đăng nhập khác')
 
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Xin hãy dùng địa chỉ email khác')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    password2 = PasswordField(
        'Nhập lại mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Yêu cầu đặt lại mật khẩu')