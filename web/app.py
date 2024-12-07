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


# login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()  # Open connection once
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if the user is an admin
            cursor.execute("SELECT * FROM admin WHERE admin_email=%s AND admin_passwd=%s", (email, password))
            admin = cursor.fetchone()

            if admin:
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

            # Check if the user is a student
            cursor.execute("SELECT * FROM student_details WHERE std_email=%s AND std_passwd=%s", (email, password))
            student = cursor.fetchone()

            if student:  # Redirect to the student dashboard
                return redirect(url_for('student_dashboard', student_id=student['std_id']))

            # Invalid credentials
            flash('Invalid email or password', 'danger')

        finally:
            conn.close()  # Ensure that the connection is closed after both queries

    return render_template('auth/login.html')


#!student = register
@app.route('/register')
def register():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM batch_details")
    batches  = cursor.fetchall()
    conn.close()
    
    return render_template('auth/register.html',batches= batches)

# # #! attendance
# @app.route('/attendance')
# def attendance():
#     # You can add logic here to fetch student-specific attendance details
#     return render_template('student/attendance.html')
# # student profile
# # Mock student data
# student_data = {
#     "name": "Alice Johnson",
#     "email": "alice.johnson@example.com",
#     "roll_number": "CS2024001",
#     "department": "Computer Science",
#     "device": "Laptop",
#     "session": "2023-2024",
#     "courses": ["Programming Fundamentals", "Database Management", "Web Development"]
# }


# @app.route('/student/attendance/<int:student_id>')
# def attendance(a_id):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
    
#      # Get session details along with course and batch details
#     cursor.execute("""
#         SELECT 
#             s.s_id, 
#             s.s_date, 
#             s.s_start_time,
#             s.s_end_time,
#             c.course_name, 
#             b.bat_name 
#         FROM session_details s
#         JOIN course_details c ON s.course_id = c.course_id
#         JOIN batch_details b ON c.bat_id = b.bat_id
#         WHERE s.s_id = %s
#     """, (s_id,))
#     session_details = cursor.fetchone()
    
#     # You can add logic here to fetch student-specific attendance details
#     return render_template('student/attendance.html')
# # student profile
# # Mock student data
# student_data = {
#     "name": "Alice Johnson",
#     "email": "alice.johnson@example.com",
#     "roll_number": "CS2024001",
#     "department": "Computer Science",
#     "device": "Laptop",
#     "session": "2023-2024",
#     "courses": ["Programming Fundamentals", "Database Management", "Web Development"]
# }

# @app.route("/profile")
# def profile():
#     """Render the profile page."""
#     return render_template("/student/profile.html", student=student_data)

# # profile updates
# @app.route("/profile_update", methods=["GET", "POST"])
# def update_profile():
#     """Render and process the profile update form."""
#     if request.method == "POST":
#         # Update student data
#         student_data["name"] = request.form["name"]
#         student_data["email"] = request.form["email"]
#         student_data["device"] = request.form["device"]
#         student_data["session"] = request.form["session"]
#         student_data["courses"] = request.form["courses"].split(",")  # Split courses by commas
#         return redirect(url_for("/profile_update"))
#     return render_template("/student/profile_update.html", student=student_data)


# # Student dashboard route
# @app.route('/student/dashboard/<int:student_id>')
# def student_dashboard(student_id):
#     # Fetch student-specific data if required using the student_id
#     # return render_template('stshboard.hudent/datml', student_id=student_id)
#     return render_template('student/dashboard.html', student_id=student_id)




# Admin dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch counts for dashboard
    cursor.execute("SELECT COUNT(*) as count FROM course_details")
    courses_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM batch_details")
    batches_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM session_details")
    sessions_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM student_details")
    students_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM device_details")
    devices_count = cursor.fetchone()['count']

    conn.close()

    return render_template(
        'admin/dashboard.html',
        courses_count=courses_count,
        batches_count=batches_count,
        sessions_count=sessions_count,
        students_count=students_count,
        devices_count=devices_count
    )


@app.route('/admin/batches')
def batches():
    # Fetch all batches
    conn = get_db_connection()  # Establish connection
    cursor = conn.cursor(dictionary=True)  # Ensure results are dictionaries
    cursor.execute("SELECT * FROM batch_details")
    batches = cursor.fetchall()
    return render_template('admin/batches.html', batches=batches)
    


@app.route('/admin/create_batch', methods=['GET', 'POST'])
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
        return redirect('/admin/batches')

    
@app.route('/admin/edit_batch/<int:bat_id>', methods=['GET', 'POST'])
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
        return redirect('/admin/batches')

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


@app.route('/admin/deactivate_batch/<int:bat_id>', methods=['GET'])
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

    return redirect('/admin/batches')


# Route to display courses and handle course creation
@app.route('/admin/courses', methods=['GET', 'POST'])
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
@app.route('/admin/edit_course/<int:course_id>', methods=['GET', 'POST'])
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
            return redirect('/admin/courses')
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
@app.route('/admin/deactivate_course/<int:course_id>', methods=['GET'])
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

    return redirect('/admin/courses')

@app.route('/admin/students', methods=['GET'])
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

@app.route('/admin/student_details/<int:std_id>', methods=['GET', 'POST'])
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
            return redirect('/admin/students')
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

@app.route('/admin/devices', methods=['GET'])
def view_devices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all devices
    cursor.execute("SELECT * FROM device_details")
    devices = cursor.fetchall()
    
    conn.close()
    return render_template('admin/devices.html', devices=devices)

@app.route('/admin/update_device/<int:device_id>', methods=['GET', 'POST'])
def update_device(device_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Get updated data from form
        device_name = request.form['device_name']
        device_mac = request.form['device_mac']
        device_status = int(request.form['device_status'])
        
        try:
            cursor.execute(
                "UPDATE device_details SET device_name = %s, device_mac = %s, device_status = %s WHERE device_id = %s",
                (device_name, device_mac, device_status, device_id)
            )
            conn.commit()
            flash("Device updated successfully!", "success")
            return redirect('/admin/devices')
        except mysql.connector.Error as e:
            flash(f"Error updating device: {str(e)}", "danger")
    
    # Fetch the current device details
    cursor.execute("SELECT * FROM device_details WHERE device_id = %s", (device_id,))
    device = cursor.fetchone()
    
    conn.close()
    return render_template('admin/update_device.html', device=device)

@app.route('/admin/delete_device/<int:device_id>', methods=['GET'])
def delete_device(device_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM device_details WHERE device_id = %s", (device_id,))
        conn.commit()
        flash("Device deleted successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Error deleting device: {str(e)}", "danger")
    
    conn.close()
    return redirect('/admin/devices')

@app.route('/admin/session/create', methods=['GET', 'POST'])
def create_session():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        course_id = request.form['course_id']
        s_date = request.form['s_date']
        s_start_time = request.form['s_start_time']
        s_end_time = request.form['s_end_time']
        make_attendance = request.form.get('make_attendance', 0)  # Default is 0 if not selected

        # Validate if the course_id exists in course_details
        cursor.execute("SELECT COUNT(*) AS count FROM course_details WHERE course_id = %s", (course_id,))
        course_exists = cursor.fetchone()['count']

        if not course_exists:
            flash("Selected course does not exist.", "danger")
            return redirect('/admin/session/create')

        try:
            cursor.execute(
                """INSERT INTO session_details 
                (course_id, s_date, s_start_time, s_end_time, make_attendance) 
                VALUES (%s, %s, %s, %s, %s)""",
                (course_id, s_date, s_start_time, s_end_time, make_attendance)
            )
            conn.commit()
            flash("Session created successfully!", "success")
            return redirect('/admin/sessions')
        except mysql.connector.Error as e:
            flash(f"Error creating session: {str(e)}", "danger")
    else:
        # Fetch courses for the dropdown
        cursor.execute("SELECT course_id, course_name FROM course_details")
        courses = cursor.fetchall()

    conn.close()
    return render_template('admin/session_create.html', courses=courses)

@app.route('/admin/sessions', methods=['GET'])
def sessions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch session details with course names
    cursor.execute("""
        SELECT 
            sd.s_id, 
            cd.course_name, 
            sd.s_date, 
            sd.s_start_time, 
            sd.s_end_time, 
            sd.make_attendance 
        FROM session_details sd
        JOIN course_details cd ON sd.course_id = cd.course_id
    """)
    sessions = cursor.fetchall()
    
    conn.close()
    return render_template('admin/sessions.html', sessions=sessions)

@app.route('/admin/session/<int:session_id>/edit', methods=['GET', 'POST'])
def edit_session(session_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        course_id = request.form['course_id']
        s_date = request.form['s_date']
        s_start_time = request.form['s_start_time']
        s_end_time = request.form['s_end_time']
        make_attendance = request.form.get('make_attendance', 0)

        try:
            cursor.execute("""
                UPDATE session_details
                SET course_id = %s, s_date = %s, s_start_time = %s, s_end_time = %s, make_attendance = %s
                WHERE s_id = %s
            """, (course_id, s_date, s_start_time, s_end_time, make_attendance, session_id))
            conn.commit()
            flash("Session updated successfully!", "success")
            return redirect('/admin/sessions')
        except mysql.connector.Error as e:
            flash(f"Error updating session: {str(e)}", "danger")
    else:
        # Fetch session details for the form
        cursor.execute("SELECT * FROM session_details WHERE s_id = %s", (session_id,))
        session = cursor.fetchone()

        # Fetch courses for the dropdown
        cursor.execute("SELECT course_id, course_name FROM course_details")
        courses = cursor.fetchall()

    conn.close()
    return render_template('admin/session_edit.html', session=session, courses=courses)

@app.route('/admin/session/<int:session_id>/delete', methods=['POST'])
def delete_session(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM session_details WHERE s_id = %s", (session_id,))
        conn.commit()
        flash("Session deleted successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Error deleting session: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect('/admin/sessions')

@app.route('/admin/session/<int:s_id>/attendance')
def view_attendance(s_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get session details along with course and batch details
    cursor.execute("""
        SELECT 
            s.s_id, 
            s.s_date, 
            s.s_start_time,
            s.s_end_time,
            c.course_name, 
            b.bat_name 
        FROM session_details s
        JOIN course_details c ON s.course_id = c.course_id
        JOIN batch_details b ON c.bat_id = b.bat_id
        WHERE s.s_id = %s
    """, (s_id,))
    session_details = cursor.fetchone()

    if not session_details:
        flash("Session not found.", "danger")
        return redirect('/admin/sessions')

    # Get all students in the batch, ordered by their roll number
    cursor.execute("""
        SELECT 
            sd.std_id, 
            sd.std_rollno, 
            sd.std_name, 
            sd.std_email, 
            sa.login_time, 
            sa.logout_time 
        FROM student_details sd
        LEFT JOIN student_attendance sa 
            ON sd.std_id = sa.std_id AND sa.s_id = %s
        WHERE sd.bat_id = (
            SELECT c.bat_id
            FROM session_details s
            JOIN course_details c ON s.course_id = c.course_id
            WHERE s.s_id = %s
        )
        ORDER BY sd.std_rollno
    """, (s_id, s_id))
    students = cursor.fetchall()

    conn.close()

    return render_template(
        'admin/attendance_view.html', 
        session=session_details, 
        students=students
    )


if __name__ == '__main__':
    app.run(debug=True)
