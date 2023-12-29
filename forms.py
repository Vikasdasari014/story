from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField


class CreatePostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    image = StringField("Image", validators=[DataRequired(), URL()])
    body1 = CKEditorField("Summery", validators=[DataRequired()])
    body2 = CKEditorField("Cast", validators=[DataRequired()])
    submit = SubmitField("post content")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign me in! ")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log Me In! ")
