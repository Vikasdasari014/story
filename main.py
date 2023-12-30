from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from forms import CreatePostForm, RegisterForm, LoginForm
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)


login_manger = LoginManager()
login_manger.init_app(app)


@login_manger.user_loader
def load_user(user_id):
    return db.get_or_404(MovieUser, user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///data.db")
db = SQLAlchemy()
db.init_app(app)


class MoviePost(db.Model):
    __tablename__ = "movie_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    img = db.Column(db.String(250), nullable=False)
    body1 = db.Column(db.Text, nullable=False)
    body2 = db.Column(db.Text, nullable=False)


class MovieUser(UserMixin, db.Model):
    __tablename__ = "m_users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorator_function

@app.route("/")
def home():
    result = db.session.execute(db.select(MoviePost))
    posts = result.scalars().all()
    return render_template("index.html", posts=posts, current_user=current_user)


@app.route("/add", methods=['GET', 'POST'])
@admin_only
def add_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = MoviePost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            img=form.image.data,
            body1=form.body1.data,
            body2=form.body2.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("newpost.html", form=form, current_user=current_user, p=1)


@app.route("/post/<int:post_id>")
def post(post_id):
    required_post = db.get_or_404(MoviePost, post_id)
    return render_template("post.html", post=required_post, current_user=current_user)


@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = db.session.execute(db.Select(MovieUser).where(MovieUser.email == form.email.data)).scalar()
        if user:
            flash("This email already in use, Login instead.")
            return redirect(url_for('login'))
        else:
            hash_and_salted_password = generate_password_hash(
                password=form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            new_user = MovieUser(
                email=form.email.data,
                password=hash_and_salted_password,
                name=form.name.data
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("register.html", form=form, p=2)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.Select(MovieUser).where(MovieUser.email == form.email.data)).scalar()
        if not user:
            flash("This email does not exist, Please try again.")
            return redirect(url_for('login'))
        if not check_password_hash(user.password, form.password.data):
            flash("Incorrect password, Please try again.")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("register.html", form=form, p=3)


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit(post_id):
    post = db.get_or_404(MoviePost, post_id)
    form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        image=post.img,
        body1=post.body1,
        body2=post.body2
    )
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.img = form.image.data
        post.body1 = form.body1.data
        post.body2 = form.body2.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("newpost.html", form=form, current_user=current_user, p=4)


@app.route("/delete/<int:post_id>")
@admin_only
def delete(post_id):
    post_delete = db.get_or_404(MoviePost, post_id)
    db.session.delete(post_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=False)
