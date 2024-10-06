from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Email, EqualTo,Length,Regexp,ValidationError,NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
import re



def custom_email_checker(form,field):
    user=User.query.filter_by(email=field.data).first()
    if user is not None:
        raise ValidationError("This email is already exists.")


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(),custom_email_checker])
    password = PasswordField('Password', validators=[DataRequired(),
        Regexp(r'.*[A-Z].*', message='Password must contain at least one uppercase letter'),
        Regexp(r'.*[a-z].*', message='Password must contain at least one lowercase letter'),
        Regexp(r'.*[0-9].*', message='Password must contain at least one digit'),
        Regexp(r'.*[@#$].*', message='Password must contain at least one special character (@, #, $, etc.)')])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

# def validate_password(self, password):
#         password = password.data
#         if not re.search(r'[a-z]', password):
#             raise ValidationError('Password must contain at least one lowercase letter.')
#         if not re.search(r'[A-Z]', password):
#             raise ValidationError('Password must contain at least one uppercase letter.')
#         if not re.search(r'[0-9]', password):
#             raise ValidationError('Password must contain at least one digit.')
#         if not re.search(r'[@#$]', password):
#             raise ValidationError('Password must contain at least one special character from @#$.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])




class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    discount_price = DecimalField('DiscountPrice', validators=[DataRequired()])
    image_url = StringField('ImageUrl',validators=[DataRequired()])
    category = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    
    
    

class ReviewForm(FlaskForm):
    content = TextAreaField('Review', validators=[DataRequired()])
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Submit Review')