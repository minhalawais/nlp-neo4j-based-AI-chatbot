from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, current_user
from requests import get
import random
import string
import database
from email.message import EmailMessage
import smtplib
import userData

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userData.userEmail = request.form.get("email")
        password = request.form.get("password")
        user = database.check_email(userData.userEmail)
        if user:
            or_pass = database.get_pass(userData.userEmail)
            if check_password_hash(or_pass, password):
                flash("Logged in successfuly!", category="success")
                curr_ip = get('https://api.ipify.org').content.decode('utf8')
                old_ip = database.get_ip(userData.userEmail)
                if curr_ip == old_ip:
                    pass
                else:
                    database.update_ip(userData.userEmail, curr_ip)
                return render_template("home.html", user=current_user)
            else:
                flash("Incorrect password!", category="error")
        else:
            flash("User does not exist!", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        password_confirm = request.form.get("password-confirm")

        #user = User.query.filter_by(email=email).first()
        user = database.check_email(email)
        if user:
            flash("Email already exist!", category="error")
        elif len(email) < 4:
            flash("Email is invalid!", category="error")
        elif len(name) < 4:
            flash("Name is less than 4 characters!", category="error")
        elif len(password) < 8:
            flash("Name is less than 8 characters!", category="error")
        elif password != password_confirm:
            flash("Passwords don\'t mach!", category="error")
        else:
            ip = get('https://api.ipify.org').content.decode('utf8')

            database.Create_user(uemail=email, uname=name, upass=generate_password_hash(password, method="sha256"), ip_add = ip)
            database.set_gender(email, database.predict_gender(name))
            flash("Created account successfuly", category="success")
            return redirect(url_for("auth.login"))

    return render_template("register.html", user=current_user)

@auth.route('/forget')
def forgot_password():
    return render_template('forgot_password.html')

@auth.route('/forgot_password', methods=['POST'])
def reset_password():
    email = request.form['email']
    user = database.check_email(email)
    if user:
        global otp
        otp = generate_otp()
        send_otp_email(email)
    else:
        flash("Email Not Found!", category="error")
        return render_template('forgot_password.html')
    flash("OTP has been sent to your email",category="success")
    return render_template('verify_otp.html')

@auth.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']
    if user_otp == otp:
        return render_template('reset_password.html')
    else:
        flash("Invalid OTP!",category="error")
        return render_template('verify_otp.html')

@auth.route('/update_password', methods=['POST'])
def update_password():
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    if len(new_password) < 8:
        flash("Password is less than 8 characters!", category="error")
        return render_template('reset_password.html')
    if new_password != confirm_password:
        flash("Password does not match!", category="error")
        return render_template('reset_password.html')
    else:
        database.update_password(userData.userEmail, generate_password_hash(new_password, method="sha256"))
        return redirect(url_for("auth.login"))

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email):
    global otp
    otp  = generate_otp()
    msg = EmailMessage()
    msg.set_content(f'Please use the verification code below to sign in.\n{otp}\nIf you didn’t request this, you can ignore this email.\nThanks')
    msg['Subject'] = 'OTP - FORGOT PASSWORD'
    msg['From'] = "minhalawais1@gmail.com"
    msg['To'] = email
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("minhalawais1@gmail.com", "faodpckumtfcmctm")
    s.send_message(msg)
    s.quit()

def getemail(mail):
    return mail

