from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import sqlite3, pyotp, pyqrcode, io, base64

app = Flask(__name__)
app.secret_key = "ultimate_cipher_gate_key_2024"
bcrypt = Bcrypt(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        email TEXT UNIQUE, 
        password TEXT, 
        role TEXT, 
        twofa_secret TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- Security Helper Functions ---
def abort_access_denied():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Access Denied</title></head>
    <body style="background:#0b0f1a; color:white; font-family:sans-serif; text-align:center; padding-top:10vh;">
        <div style="font-size:5rem; margin-bottom:20px;">🛑</div>
        <h1 style="color:#ef4444; letter-spacing: 2px;">ACCESS DENIED</h1>
        <p style="color:#94a3b8;">Your account does not have permission to access this endpoint.</p>
        <p style="color:#475569; font-size: 0.8rem;">This incident will be logged.</p>
        <br><br>
        <a href="/dashboard" style="padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">← RETURN TO DASHBOARD</a>
    </body>
    </html>
    """
    return html, 403

@app.errorhandler(404)
def page_not_found(e):
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Restricted / Not Found</title></head>
    <body style="background:#0b0f1a; color:white; font-family:sans-serif; text-align:center; padding-top:10vh;">
        <div style="font-size:5rem; margin-bottom:20px;">🛡️</div>
        <h1 style="color:#f59e0b; letter-spacing: 2px;">RESTRICTED OR NOT FOUND</h1>
        <p style="color:#94a3b8;">The endpoint you are trying to reach does not exist or is highly restricted.</p>
        <br><br>
        <a href="/dashboard" style="padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">← RETURN TO DASHBOARD</a>
    </body>
    </html>
    """
    return html, 404

@app.route('/')
def index(): return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pw = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        secret = pyotp.random_base32()
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO users (name, email, password, role, twofa_secret) VALUES (?,?,?,?,?)',
                         (request.form['name'], request.form['email'], pw, request.form['role'], secret))
            conn.commit()
            session['setup_user_id'] = cur.lastrowid
            conn.close()
            return redirect(url_for('setup_2fa'))
        except:
            flash("Registration Failed: Email might exist.")
    return render_template('register.html')

@app.route('/setup_2fa', methods=['GET', 'POST'])
def setup_2fa():
    if 'setup_user_id' not in session: return redirect(url_for('register'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id=?', (session['setup_user_id'],)).fetchone()
    conn.close()
    
    # Create QR Code
    totp = pyotp.TOTP(user['twofa_secret'])
    qr = pyqrcode.create(totp.provisioning_uri(name=user['email'], issuer_name="Sentinel Hub"))
    buf = io.BytesIO()
    qr.png(buf, scale=5)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    if request.method == 'POST':
        session.pop('setup_user_id', None)
        flash("Registration complete! Please login with your new Authenticator Code.")
        return redirect(url_for('login')) 
        
    # هنا قمنا بإرسال الـ secret_key لصفحة الـ HTML
    return render_template('setup_2fa.html', qr_code=qr_b64, secret_key=user['twofa_secret'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email=?', (request.form['email'],)).fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            session['temp_user_id'] = user['id']
            return redirect(url_for('verify_2fa'))
        flash("Wrong credentials")
    return render_template('login.html')

@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'temp_user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id=?', (session['temp_user_id'],)).fetchone()
    conn.close()
    if request.method == 'POST':
        if pyotp.TOTP(user['twofa_secret']).verify(request.form['code']):
            session.pop('temp_user_id')
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            return redirect(url_for('dashboard'))
        flash("Incorrect 2FA Code")
    return render_template('verify_2fa.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['name'], role=session['role'])

@app.route('/admin_page')
@app.route('/admin')
@app.route('/Admin')
def admin_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    if session.get('role') != 'Admin': return abort_access_denied()
    
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall() 
    conn.close()
    return render_template('admin_page.html', users=users)

@app.route('/manager_page')
@app.route('/manager')
@app.route('/Manager')
def manager_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    if session.get('role') not in ['Admin', 'Manager']: return abort_access_denied()
        
    conn = get_db_connection()
    users = conn.execute('SELECT name, email, role FROM users').fetchall()
    conn.close()
    return render_template('manager_page.html', users=users)

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/update_role/<int:target_id>', methods=['POST'])
def update_role(target_id):
    if session.get('role') != 'Admin': return abort_access_denied()
        
    new_role = request.form.get('new_role')
    conn = get_db_connection()
    conn.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, target_id))
    conn.commit()
    conn.close()
    
    flash(f"User role updated to {new_role} successfully!")
    return redirect(url_for('admin_page'))

@app.route('/delete_user/<int:target_id>', methods=['POST'])
def delete_user(target_id):
    if session.get('role') != 'Admin': return abort_access_denied()
        
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (target_id,))
    conn.commit()
    conn.close()
    flash("User has been permanently removed from the system.")
    return redirect(url_for('admin_page'))

if __name__ == '__main__': app.run(debug=True)