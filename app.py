from flask import Flask, render_template, request, redirect, url_for
import hashlib

app = Flask(__name__, template_folder='.')

# This is a temporary fake database. 
# In a real startup, you would use PostgreSQL or SQLite.
users_db = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
# app.py

# ... imports and setup ...

# 1. THE LOGIN ROUTE (Redirects to Dashboard on success)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check against your database
        if email in users_db and users_db[email]['password'] == password:
            # SUCCESS: Render the dashboard and pass the email as 'username'
            return render_template('dashboard.html', username=email)
        else:
            return "Wrong password. <a href='/login'>Try Again</a>"

    return render_template('login.html')

# 2. THE DASHBOARD ROUTE (So the page exists)
@app.route('/dashboard')
def dashboard():
    # In a real app, check if user is logged in here!
    return render_template('dashboard.html', username="Guest")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Get the Role (Individual vs Society)
        role = request.form.get('role')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 2. Get Specific Data based on Role
        user_data = {
            'role': role,
            'password': password, # In real app: bcrypt.hashpw(password)
            'email': email
        }

        if role == 'society':
            user_data['org_name'] = request.form.get('org_name')
            user_data['reg_id'] = request.form.get('reg_id')
            # Extra Logic: Verify if the Registration ID (ICE) is valid via API
        else:
            user_data['fullname'] = request.form.get('fullname')

        # 3. Save to Database
        users_db[email] = user_data
        
        print(f"New User Registered: {user_data}") # See this in VS Code terminal
        return redirect(url_for('login'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
