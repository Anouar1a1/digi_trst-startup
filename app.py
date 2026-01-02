from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import qrcode
import os

app = Flask(__name__, template_folder='.')

# NEW: This secret key is required to sign the "ID Badge" (Session Cookie)
# In a real startup, make this a long random string.
app.secret_key = 'super_secret_startup_key'

# Create folder for QRs
if not os.path.exists('static/qrcodes'):
    os.makedirs('static/qrcodes')

users_db = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users_db and users_db[email]['password'] == password:
            # --- THE FIX IS HERE ---
            # Instead of just showing the page, we give them an ID badge (Session)
            session['user'] = email 
            return redirect(url_for('dashboard'))
        else:
            return "Wrong password. <a href='/login'>Try Again</a>"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # 1. CHECK ID BADGE
    if 'user' in session:
        # If they have a badge, use their real name
        current_user = session['user']
        return render_template('dashboard.html', username=current_user)
    else:
        # If no badge, kick them back to login!
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Tear up the ID badge
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # SECURITY UPGRADE: Hash the password before saving!
        # "pbkdf2:sha256" is a standard, strong encryption method.
        secure_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # We save 'secure_password' (the scrambled mess), NOT 'password'
        users_db[email] = {'password': secure_password, 'role': role}
        
        print(f"User saved with hash: {secure_password}") # Check your terminal to see the difference!
        return redirect(url_for('login'))

    return render_template('register.html')
@app.route('/generate_certificate', methods=['POST'])
def generate_certificate():
    # Security Check: Are they logged in?
    if 'user' not in session:
        return redirect(url_for('login'))
        
    name = request.form.get('student_name')
    degree = request.form.get('degree_title')
    date = request.form.get('date_issued')
    
    raw_data = f"{name}{degree}{date}SECRET"
    cert_hash = hashlib.sha256(raw_data.encode()).hexdigest()
    verify_url = f"http://digitrst.com/verify/{cert_hash}"
    
    img = qrcode.make(verify_url)
    filename = f"static/qrcodes/{cert_hash}.png"
    img.save(filename)
    
    return f"""
    <body style="background:#0f172a; color:white; text-align:center; padding:50px; font-family:sans-serif;">
        <h1 style="color:#d4af37">Certificate Signed!</h1>
        <p>Issuer: {session['user']}</p>
        <img src="/{filename}" style="border:10px solid white; margin:20px;">
        <br>
        <a href="/dashboard" style="color:#d4af37">Back to Dashboard</a>
    </body>
    """

if __name__ == '__main__':
    app.run(debug=True)
