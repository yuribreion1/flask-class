from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import backref
from flask_login import LoginManager, UserMixin, login_required, login_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'secret'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def current_user(user_id):
   return User.query.get(user_id)

db = SQLAlchemy(app)
Bootstrap(app)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(84), nullable=False)
    email = db.Column(db.String(84), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False)

    def __str__(self):
        return self.name

class Profile(db.Model):
   __tablename__ = "profiles"
   id = db.Column(db.Integer, primary_key=True)
   photo = db.Column(db.Unicode(124), nullable=False)
   user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


@app.route('/')
def index():
    return render_template("login.html")

@login_required
@app.route('/home')
def home():
   return render_template("home.html")

@app.route('/users')
def get_users():
   users = User.query.all() # getting all users
   return render_template("users.html", users=users)

@app.route('/user/<int:id>')
def get_user(id):
   user = User.query.get(id)
   return render_template("user.html", user=user)

@app.route('/user/delete/<int:id>') # passing id to delete
def delete_user(id):
   user = User.query.filter_by(id=id).first()
   db.session.delete(user)
   db.session.commit()
   return redirect("/users")

@app.route('/register', methods=["GET","POST"])
def register_user():
   if request.method == "POST":
      user = User()
      user.name = request.form["name"]
      user.email = request.form["email"]
      user.password = generate_password_hash(request.form["password"])
      db.session.add(user)
      db.session.commit()
      return redirect(url_for("index"))
   return render_template("register.html")

@app.route('/login', methods=["GET","POST"])
def login():
   if request.method == "POST":
      email = request.form["email"]
      password = request.form["password"]

      user = User.query.filter_by(email=email).first()
      errors = {}

      if not user:
         errors["error"] = "Invalid credentials"
         return redirect("login.html")
      if not check_password_hash(user.password, password):
         errors["error"] = "Invalid credentials"
         return redirect("login.html")

      login_user(user)
      return redirect(url_for("home"))

   return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)