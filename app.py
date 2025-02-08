from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "SOME_RANDOM_SECRET"

users_db = {}

@app.route('/')
def home():
    return "Welcome! Go to /register or /login."

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users_db:
            return "Username already taken."

        users_db[username] = generate_password_hash(password)
        return "Registration successful! Go to /login."

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_hash = users_db.get(username)
        if not user_hash or not check_password_hash(user_hash, password):
            return "Invalid username or password."

        session['username'] = username
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return "You are not logged in."

    return f"Hello, {session['username']}! This is your dashboard."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
