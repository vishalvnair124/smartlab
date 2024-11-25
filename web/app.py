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




# Route to display courses and handle course creation
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    conn = get_db_connection()  # Establish connection
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for ease of access

    if request.method == 'POST':
        # Handle course creation as before
        course_name = request.form['course_name']
        bat_id = request.form['bat_id']
        course_status = 1  # Default active status

        try:
            # Insert course into database
            cursor.execute("INSERT INTO course_details (course_name, bat_id, course_status) VALUES (%s, %s, %s)",
                           (course_name, bat_id, course_status))
            conn.commit()
            flash("Course created successfully!", "success")
        except mysql.connector.Error as e:
            flash(f"Error creating course: {str(e)}", "danger")
        finally:
            conn.close()

    # Fetch all courses with batch names (JOIN query)
    cursor.execute("""
        SELECT course_details.course_id, course_details.course_name, course_details.bat_id, 
               batch_details.bat_name, course_details.course_status
        FROM course_details
        JOIN batch_details ON course_details.bat_id = batch_details.bat_id
    """)
    courses = cursor.fetchall()

    # Fetch active batches for the dropdown (only active batches)
    cursor.execute("SELECT * FROM batch_details WHERE bat_status = 1")  # Only active batches
    batches = cursor.fetchall()

    conn.close()

    return render_template('admin/courses.html', courses=courses, batches=batches)



# Route to edit a course
@app.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Handle course edit
        course_name = request.form['course_name']
        bat_id = request.form['bat_id']
        course_status = request.form['course_status']  # Getting the status from the form

        try:
            cursor.execute("""
                UPDATE course_details
                SET course_name = %s, bat_id = %s, course_status = %s
                WHERE course_id = %s
            """, (course_name, bat_id, course_status, course_id))
            conn.commit()
            flash("Course updated successfully!", "success")
            return redirect('/courses')
        except mysql.connector.Error as e:
            flash(f"Error updating course: {str(e)}", "danger")
    
    # Fetch course details for editing
    cursor.execute("SELECT * FROM course_details WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()

    # Fetch active batches for dropdown
    cursor.execute("SELECT * FROM batch_details WHERE bat_status = 1")
    batches = cursor.fetchall()

    conn.close()

    return render_template('admin/edit_course.html', course=course, batches=batches)



# Route to deactivate a course
@app.route('/deactivate_course/<int:course_id>', methods=['GET'])
def deactivate_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE course_details SET course_status = 0 WHERE course_id = %s", (course_id,))
        conn.commit()
        flash("Course deactivated successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Error deactivating course: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect('/courses')

@app.route('/students', methods=['GET'])
def students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all students along with their batch name
    cursor.execute("""
        SELECT student_details.std_id, student_details.std_name, student_details.std_rollno, 
               batch_details.bat_name, student_details.std_status
        FROM student_details
        JOIN batch_details ON student_details.bat_id = batch_details.bat_id
    """)
    students = cursor.fetchall()

    conn.close()
    return render_template('admin/students.html', students=students)

@app.route('/student_details/<int:std_id>', methods=['GET', 'POST'])
def student_details(std_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Handle activation/deactivation
        action = request.form['action']
        new_status = 1 if action == 'activate' else 0
        
        try:
            cursor.execute("UPDATE student_details SET std_status = %s WHERE std_id = %s", 
                           (new_status, std_id))
            conn.commit()
            flash(f"Student {'activated' if action == 'activate' else 'deactivated'} successfully!", "success")
            return redirect('/students')
        except mysql.connector.Error as e:
            flash(f"Error updating student status: {str(e)}", "danger")

    # Fetch student details
    cursor.execute("""
        SELECT student_details.std_id, student_details.std_name, student_details.std_rollno, 
               student_details.std_email, student_details.std_passwd, batch_details.bat_name, 
               student_details.std_status
        FROM student_details
        JOIN batch_details ON student_details.bat_id = batch_details.bat_id
        WHERE student_details.std_id = %s
    """, (std_id,))
    student = cursor.fetchone()

    conn.close()

    return render_template('admin/student_details.html', student=student)



if __name__ == '__main__':
    app.run(debug=True)
