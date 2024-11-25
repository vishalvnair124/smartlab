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




# Student dashboard route
@app.route('/student/dashboard/<int:student_id>')
def student_dashboard(student_id):
    # Fetch student-specific data if required using the student_id
    return render_template('student/dashboard.html', student_id=student_id)


# Admin dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query counts from the database
    cursor.execute("SELECT COUNT(*) FROM course_details")
    courses_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM batch_details")
    batches_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM session_details")
    sessions_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM student_details")
    students_count = cursor.fetchone()[0]

    conn.close()

    # Pass counts to the template
    return render_template('admin/dashboard.html',
                           courses_count=courses_count,
                           batches_count=batches_count,
                           sessions_count=sessions_count,
                           students_count=students_count)

@app.route('/courses')
def courses():
    # Fetch and display course details
    return render_template('admin/courses.html')

@app.route('/batches')
def batches():
    # Fetch all batches
    conn = get_db_connection()  # Establish connection
    cursor = conn.cursor(dictionary=True)  # Ensure results are dictionaries
    cursor.execute("SELECT * FROM batch_details")
    batches = cursor.fetchall()
    return render_template('admin/batches.html', batches=batches)
    

@app.route('/sessions')
def sessions():
    # Fetch and display session details
    return render_template('admin/sessions.html')

@app.route('/students')
def students():
    # Fetch and display student details
    return render_template('admin/students.html')


@app.route('/create_batch', methods=['GET', 'POST'])
def manage_batches():
    conn = get_db_connection()  # Establish connection
    cursor = conn.cursor(dictionary=True)  # Ensure results are dictionaries
    if request.method == 'POST':
        # Insert new batch
        bat_name = request.form['bat_name']
        bat_status = 1
        cursor.execute("INSERT INTO batch_details (bat_name, bat_status) VALUES (%s, %s)", (bat_name, bat_status))
        conn.commit()
        flash("Batch created successfully!", "success")
        return redirect('/batches')

    
@app.route('/edit_batch/<int:bat_id>', methods=['GET', 'POST'])
def edit_batch(bat_id):
    conn = get_db_connection()  # Establish database connection
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for ease of access

    if request.method == 'POST':
        # Update batch
        bat_name = request.form['bat_name']
        bat_status = request.form['bat_status']

        try:
            cursor.execute(
                "UPDATE batch_details SET bat_name = %s, bat_status = %s WHERE bat_id = %s",
                (bat_name, bat_status, bat_id)
            )
            conn.commit()
            flash("Batch updated successfully!", "success")
        except mysql.connector.Error as e:
            flash(f"Error updating batch: {str(e)}", "danger")
        finally:
            conn.close()  # Ensure connection is closed
        return redirect('/batches')

    try:
        # Fetch batch details for editing
        cursor.execute("SELECT * FROM batch_details WHERE bat_id = %s", (bat_id,))
        batch = cursor.fetchone()
    except mysql.connector.Error as e:
        flash(f"Error fetching batch: {str(e)}", "danger")
        batch = None
    finally:
        conn.close()

    return render_template('admin/edit_batch.html', batch=batch)


@app.route('/deactivate_batch/<int:bat_id>', methods=['GET'])
def deactivate_batch(bat_id):
    conn = get_db_connection()  # Establish database connection
    cursor = conn.cursor()

    try:
        # Update batch status to inactive (0)
        cursor.execute("UPDATE batch_details SET bat_status = 0 WHERE bat_id = %s", (bat_id,))
        conn.commit()
        flash("Batch marked as inactive successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Error marking batch as inactive: {str(e)}", "danger")
    finally:
        conn.close()  # Ensure connection is closed

    return redirect('/batches')




if __name__ == '__main__':
    app.run(debug=True)
