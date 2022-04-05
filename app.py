from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from string import punctuation

from app_forms import LoginForm, UserForm, PostForm, PasswordForm, NameForm, SearchForm

app = Flask(__name__)

ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_blog'

app.config['SECRET_KEY'] = "Depok, Lombok, Palembang, and Karawang"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Database.query.get(int(user_id))

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default = datetime.utcnow)

    poster_id = db.Column(db.Integer, db.ForeignKey('database.id'))

class Database(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    username = db.Column(db.String(120), nullable = False, unique = True)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    password_hash = db.Column(db.String(128))

    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name

def password_checker(password):
    special_character = [True for a in password if a in punctuation]
    bool = True

    if ' ' in password:
        flash("There is a space in your password")
        bool = False

    if len(password) < 5:
        flash("Password must be at least 5 characters")
        bool = False

    if not any(char.isupper() for char in password):
        flash("Password must contain at least one capital letter")
        bool = False
        
    if not any(char.isdigit() for char in password):
        flash("Password must contain at least one number")
        bool = False

    if len(special_character) == 0:
        flash("Password must contain at least one special character")
        bool = False

    if bool:
        return bool

# Page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/')
def index():
    web_name = "PDT Blog"
    return render_template("index.html", web_name = web_name)

@app.route('/date')
def get_current_date():

    return {"Date": date.today()}

@app.route('/user/register', methods=['GET', 'POST'])
def register():
    name = None
    form = UserForm()

    if form.validate_on_submit():
        user = Database.query.filter_by(username = form.username.data).first()

        if user is None:

            if password_checker(form.password_hash.data):
                # Hash password
                hashed_password = generate_password_hash(form.password_hash.data, 'sha256')

                user = Database(name = form.name.data, username = form.username.data, password_hash = hashed_password)
                db.session.add(user)
                db.session.commit()

                name = form.name.data

                form.name.data = ''
                form.username.data = ''
                form.password_hash.data = ''
                flash("Successfully registered")

        else:
            flash("Username is already taken")
                
            form.username.data = ''

    our_users = Database.query.order_by(Database.date_added)
    return render_template("register.html", 
        form = form,
        name = name,
        our_users = our_users)

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", name = name)


@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    username = None
    password = None
    check_pw = None
    passed = None
    form = PasswordForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password_hash.data

        form.username.data = ''
        form.password_hash.data = ''

        check_pw = Database.query.filter_by(username = username).first()

        passed = check_password_hash(check_pw.password_hash, password)

    return render_template('test_pw.html',
        username = username,
        password = password,
        check_pw = check_pw,
        passed = passed,
        form = form
    )

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()

    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''

    return render_template('name.html',
        name = name,
        form = form
    )

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    updated = Database.query.get_or_404(id)

    if request.method == "POST":
        updated.name = request.form['name']
        updated.username = request.form['username']

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template('update.html',
                form = form,
                updated = updated)

        except:
            flash("Error! Look like there was a problem")
            return render_template('update.html',
                form = form,
                updated = updated)

    else:
        return render_template('update.html',
            form = form,
            updated = updated,
            id = id)

@app.route('/delete/<int:id>')
def delete(id):
    delete_user = Database.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(delete_user)
        db.session.commit()
        flash("User Deleted Successfully")

        our_users = Database.query.order_by(Database.date_added)
        return render_template("register.html", 
            form = form,
            name = name,
            our_users = our_users)        

    except:
        flash("There was a problem deleting the user")

        our_users = Database.query.order_by(Database.date_added)
        return render_template("register.html", 
            form = form,
            name = name,
            our_users = our_users) 

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Database.query.filter_by(username = form.username.data).first()

        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful")

                return redirect(url_for('dashboard'))
            
            else:
                flash("Wrong password - Try Again")

        else:
            flash("That User Doesn't Exist")

    return render_template('login.html', form = form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    updated = Database.query.get_or_404(id)

    if request.method == "POST":
        updated.name = request.form['name']
        updated.username = request.form['username']

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template('dashboard.html',
                form = form,
                updated = updated)

        except:
            flash("Error! Look like there was a problem")
            return render_template('dashboard.html',
                form = form,
                updated = updated)

    else:
        return render_template('dashboard.html',
            form = form,
            updated = updated,
            id = id)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out")
    return redirect(url_for('login'))

@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)

    return render_template("posts.html", posts = posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    
    return render_template("post.html", post = post)


@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title = form.title.data, poster_id = poster, content = form.content.data)

        form.title.data = ''
        form.content.data = ''

        db.session.add(post)
        db.session.commit()

        flash("Blog Post Submitted Successfully")
    
    return render_template("add_post.html", form = form)

@app.context_processor
def passing():
    form = SearchForm()

    return dict(form = form)

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data

        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        
        return render_template("search.html", 
            form = form, 
            searched = post.searched,
            posts = posts)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data

        db.session.add(post)
        db.session.commit()

        flash("Post Has Been Updated")

        return redirect(url_for('post', id = post.id))

    form.title.data = post.title
    form.content.data = post.content

    return render_template('edit_post.html', form = form)

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    deleted_post = Posts.query.get_or_404(id)
    id = current_user.id
    try:
        db.session.delete(deleted_post)
        db.session.commit()

        flash("Blog Post Was Deleted Successfully")

        posts = Posts.query.order_by(Posts.date_posted)

        return render_template("posts.html", posts = posts, id = id)

    except:
        flash("There was a problem deleting the post")

        posts = Posts.query.order_by(Posts.date_posted)

        return render_template("posts.html", posts = posts)
