from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartlab',
}

# Function to connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if the user is an admin
        cursor.execute("SELECT * FROM admin WHERE admin_email=%s AND admin_passwd=%s", (email, password))
        admin = cursor.fetchone()

        if admin:
            conn.close()
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

        # Check if the user is a student
        cursor.execute("SELECT * FROM student_details WHERE std_email=%s AND std_passwd=%s", (email, password))
        student = cursor.fetchone()
        conn.close()

        if student:
            # Redirect to the student dashboard
            return redirect(url_for('student_dashboard', student_id=student['std_id']))

        # Invalid credentials
        flash('Invalid email or password', 'danger')

    return render_template('auth/login.html')

# Admin dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

# Student dashboard route
@app.route('/student/dashboard/<int:student_id>')
def student_dashboard(student_id):
    # Fetch student-specific data if required using the student_id
    return render_template('student/dashboard.html', student_id=student_id)


if __name__ == '__main__':
    app.run(debug=True)
