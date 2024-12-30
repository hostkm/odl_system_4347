from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'your_secret_key_here'

DB_PATH = 'database.db'

# Route for login page
@app.route('/')
def index():
    return render_template('index.html')

# Route for login functionality
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT password, role FROM login WHERE username = ?', (username,))
        row = cursor.fetchone()

        if row:  # Check if the username exists
            stored_password, role = row  # Hashed password and role from DB
            if check_password_hash(stored_password, password):  # Verify the password
                session['username'] = username  # Store username in session
                session['role'] = role  # Store role in session
                return redirect(url_for('dashboard'))
            else:
                return "Error: Invalid username or password!"
        else:
            return "Error: Invalid username or password!"
    except Exception as e:
        return f"Error: {e}"

# Route for registration functionality
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Plain password
        role = request.form['role']  # Role from the form
        try:
            # Hash the password before saving it
            hashed_password = generate_password_hash(password)

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Create the login table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login (
                    username TEXT PRIMARY KEY NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                );
            ''')

            # Create the profile table if it doesn't exist
            #cursor.execute('''
                #CREATE TABLE IF NOT EXISTS profile (
                    #username TEXT PRIMARY KEY,
                    #FOREIGN KEY (username) REFERENCES login (username)
                    #first_name TEXT,
                    #last_name TEXT,
                    #email TEXT,
                    #age INTEGER
                #);
            #''')

            # Create the trigger if it doesn't exist
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS after_login_insert
                AFTER INSERT ON login
                BEGIN
                    INSERT INTO profile (username) VALUES (NEW.username);
                END;
            ''')

            # Insert the user into the login table
            cursor.execute('INSERT INTO login (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
            conn.commit()

            return render_template('index.html')
        except sqlite3.IntegrityError:
            return "Error: Username already exists!"
        except Exception as e:
            return f"Error: {e}"
    else:
        return render_template('register.html')

# Route for dashboard
@app.route('/dashboard')
def dashboard():
    username = session.get('username')  # Retrieve the username from session
    role = session.get('role')  # Retrieve the role from session

    if username and role:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM profile WHERE username = ?', (username,))
            user_profile = cursor.fetchone()  # Fetch user profile

            # Render different dashboards based on the role
            if role == 'student':
                return render_template('student_dashboard.html', username=username, user_profile=user_profile)
            elif role == 'teacher':
                return render_template('teacher_dashboard.html', username=username, user_profile=user_profile)
            elif role == 'admin':
                return render_template('admin_dashboard.html', username=username, user_profile=user_profile)
            else:
                return "Error: Role not recognized!"
        except Exception as e:
            return f"Error fetching profile: {e}"
    else:
        return redirect(url_for('index'))

# Routes for additional pages
@app.route('/collaborative-tools')
def collaborative_tools():
    return render_template('collaborative-tools.html')

@app.route('/social-media')
def social_media():
    return render_template('social-media.html')

@app.route('/gamifield-learning')
def gamified_learning():
    return render_template('gamifield-learning.html')

@app.route('/study-groups')
def study_groups():
    return render_template('study-groups.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/details')
def details():
    return render_template('details.html')

if __name__ == '__main__':
    app.run(debug=True)
