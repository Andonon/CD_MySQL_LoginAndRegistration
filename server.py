#pylint: disable=C0103,C0111
import re
from flask import Flask, render_template, redirect, request, flash, session
from flask_bcrypt import Bcrypt
from mysqlconnection import MySQLConnector

app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, 'logins')
app.secret_key = 'lkjasasdasdasdasd09809a8sdlkjasd9089'

#This is the login page
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    query = "SELECT * from users where email = :email LIMIT 1"
    data = {
        'email': request.form['email']
    }
    get_user = mysql.query_db(query, data)
    if get_user:
        flash("I see you have a user account")
        session['userid'] = get_user[0]['id']
        session['user_first_name'] = get_user[0]['first_name']
        hashed_password = get_user[0]['password']
        print "29 hashed password = ", hashed_password
        if bcrypt.check_password_hash(hashed_password, request.form['password']):
            print "31 brypt pass hash validated"
        #     session['logged_in'] = True
        #     return redirect('/home')
        else:
            print "34, failed bcrypt, exiting... "
        #     session['logged_in'] = False


        return redirect('/')
    else:
        flash("Your username (email) was not found, please try again or register")
        return redirect('/')





#This is the register page, where the user will register for an account.
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = 0
    if request.method == 'POST':
        #check first name (2 chars, submitted, and letters only)
        first_name = request.form['first_name']
        if not first_name:
            error += 1
            flash("You myst supply a First Name")
        elif not first_name.isalpha():
            error += 1
            flash("First Name must contain letters only.")
        elif len(first_name) < 3:
            error += 1
            flash("First Name must contain more than 2 characters.")
        #check last name (2 chars, submitted, and letters only)
        last_name = request.form['last_name']
        if not last_name:
            error += 1
            flash("You must supply a Last Name")
        elif not last_name.isalpha():
            error += 1
            flash("Last Name must contain letters only.")
        elif len(last_name) < 3:
            error += 1
            flash("Last Name must contain more than 2 characters.")
        #check email
        email = request.form['email']
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            error += 1
            flash("Invalid Email Address detected.")
        #check password and confirm password
        user_password = request.form['user_password']
        print "61 password", user_password
        confirm_password = request.form['confirm_password']
        print "63 confirm password:", confirm_password
        if not user_password:
            print "65 no password"
            error += 1
            flash("You must supply a password.")
        elif not confirm_password:
            print "69 no confirm password"
            error += 1
            flash("You must supply a confirm password")
        if user_password != confirm_password:
            print "73 passwords do not match (strings)"
            error += 1
            flash("Passwords do not match.")
        elif len(user_password) < 8:
            error += 1
            flash("Password must be at least 8 characters long.")
        #prior to the insert, cache and return any errors.
        if error > 0:
            return redirect('/register')
        else:
            pw_hash = bcrypt.generate_password_hash(user_password)
            query = "INSERT INTO users (first_name, last_name, email, password, created_at, \
                                        updated_at) values (:first_name, :last_name, :email, \
                                        :password, now(), now())"
            data = {
                'first_name': first_name, 'last_name': last_name, \
                'email': email, 'password': pw_hash}
            mysql.query_db(query, data)
            session['logged_in'] = True
            return redirect('/home')
    else:
        if request.method == 'GET':
        #exit on fail to main login page with flash error
            return render_template('register.html')

#This is the home page, after login with welcome message for the user that they are logged in
@app.route('/home')
def home():
    #check for session
    return render_template('home.html')

app.run(debug=True)