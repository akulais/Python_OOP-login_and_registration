from flask import Flask, request, redirect, render_template, session, flash
import re
import pprint
# import md5 # imports the md5 module to generate a hash
# import os, binascii
from flask.ext.bcrypt import Bcrypt
from mysqlconnection import MySQLConnector

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector('logins')

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    # if not (password):
    #     password = '1'
    
    if len(request.form['first_name']) < 2:
        flash(u"Your first name is too short!", 'error')
    if len(request.form['last_name']) < 2:
        flash(u"Your last name is too short!!", 'error')
    if len(request.form['email']) < 1:
        flash(u"Email cannot be empty!", 'error')
    if len(request.form['password']) < 8:
        flash(u'Password cannot be less than 8 charachters', 'error')
    if len(request.form['confirm_password']) < 1:
        flash(u'Confirm password cannot be blank', 'error')
    if request.form['confirm_password'] != request.form['password']:
        flash(u'Password and Confirm password do not match', 'error')
    if not EMAIL_REGEX.match(request.form['email']):
        flash(u"This is not a valid email Address!", 'error')
    else:
        pw_hash = bcrypt.generate_password_hash(password)
        flash(u'You have successfully registered.  Thank you','true')
        query = "INSERT INTO logins (first_name, last_name, pw_hash, email, password, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', NOW(), NOW())".format(request.form['first_name'], request.form['last_name'], pw_hash, request.form['email'], request.form['password'])
    try:
        query
        mysql.run_mysql_query(query)
        return redirect('/to_login')
    except:
        return redirect('/')

@app.route('/to_login')
def to_login():
    return render_template('/login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    
    if len(request.form['email']) < 1:
        flash(u"Email cannot be empty!", 'error')
    if len(request.form['password']) < 1:
        flash(u'Password cannot be empty!', 'error')

    user_query = "SELECT * FROM logins WHERE email = '{}' LIMIT 1".format(email)

    user = mysql.fetch(user_query)
    
    pprint.pprint(user)

    password = request.form['password']
    print password
    if bcrypt.check_password_hash(user[0]['pw_hash'],password):
        print 'here'
        flash(u'You have successfully logged in.  Thank you','true')
        return redirect('/to_login')
    else:
        print 'there'
        flash(u"It's nothing personal, or maybe it is, but I digress.  Your credentials don't match, and I don't know you personally.  So try it again.  If you can't login in after a second attempt wait a few minutes and try again.", 'error')
        return redirect('/')

@app.route('/delete/<id>')
def delete(id):
	mysql.run_mysql_query(("DELETE FROM emails WHERE id = '{}'").format(id))
	return redirect('/')

@app.route('/reset')
def reset():
	session.clear()
	return redirect("/")
app.run(debug=True)
