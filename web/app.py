from flask import Flask, render_template, request, redirect, url_for, flash, send_file,session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import mysql.connector



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smartlab1',
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
                session['user_type'] = 'admin'  # Store user type in session
                flash('Login successfully!', 'info')
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

            # Check if the user is a student
            cursor.execute("SELECT * FROM student_details WHERE std_email=%s AND std_passwd=%s", (email, password))
            student = cursor.fetchone()

            if student:
                # Store the student details in session
                session['user_type'] = 'student'
                session['student_id'] = student['std_id']
                session['student_name'] = student['std_name']

                # Check the student's verification status
                if student['std_status'] == 1:
                    flash('Login successfully!', 'info')
                    return redirect(url_for('student_dashboard', std_name=student['std_name'], student_id=student['std_id']))  # Redirect to the student dashboard
                else:
                    flash('Please wait for admin approval.', 'warning')
                    return redirect(url_for('user_verification', student_id=student['std_id']))  # Redirect to user verification page

            # Invalid credentials
            flash('Invalid email or password', 'error')

        finally:
            conn.close()  # Ensure that the connection is closed

    return render_template('auth/login.html')


# logout to clear session
@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log the user out
    flash('Logout successfully.', 'info')
    return redirect('/')

# register student
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collect form data
        std_rollno = request.form.get('std_rollno', '').strip()
        batch_id = request.form.get('bat_id', '').strip()
        std_name = request.form.get('std_name', '').strip()
        std_email = request.form.get('std_email', '').strip()
        password = request.form.get('std_passwd', '').strip()
        confirm_password = request.form.get('confirm-password', '').strip()

        # Input validation
        if not all([std_rollno, batch_id, std_name, std_email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return redirect('/register')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect('/register')

        # Database operations
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                try:
                    # Check if roll number or email already exists
                    cursor.execute("""
                        SELECT * FROM student_details 
                        WHERE std_rollno = %s OR std_email = %s
                    """, (std_rollno, std_email))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        if existing_user['std_rollno'] == std_rollno:
                            flash('Roll number is already registered.', 'error')
                        elif existing_user['std_email'] == std_email:
                            flash('Email is already registered. Please use another email.', 'error')
                        return redirect('/register')

                    # Insert user with plain text password (not recommended for production)
                    cursor.execute("""
                        INSERT INTO student_details (std_rollno, bat_id, std_name, std_email, std_passwd, std_status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (std_rollno, batch_id, std_name, std_email, password, 0))
                    conn.commit()

                    flash('Registration successful. Please log in.', 'success')
                    return redirect('/')
                except mysql.connector.Error as err:
                    flash(f'Database Error: {err}', 'error')
                    return redirect('/register')
    # Fetch batches for dropdown
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM batch_details")
            batches = cursor.fetchall()

    return render_template('auth/register.html', batches=batches)


# admin verification
@app.route('/user_verification/<int:student_id>')
def user_verification(student_id):
    # Add logic to fetch and verify user details using the provided student_id
    # Example: Fetch the student's verification status from the database

    # Connect to the database
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM student_details WHERE std_id = %s", (student_id,))
            student = cursor.fetchone()

    if not student:
        flash('Student not found.', 'error')
        return redirect('/')

    # Pass the student's verification status to the template
    return render_template('student/user_verification.html', student=student)

# profile and profile update
@app.route('/profile')
def profile():
    if 'user_type' in session and session['user_type'] == 'student':
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM student_details WHERE std_id = %s", (session['student_id'],))
                student = cursor.fetchone()
        
        if not student:
            flash('Profile not found.', 'error')
            return redirect(url_for('login'))

        return render_template('student/profile.html', student=student)
    
    flash('Unauthorized access.', 'error')
    return redirect(url_for('login'))


# Update Profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_type' in session and session['user_type'] == 'student':
        # Fetch form data
        std_name = request.form.get('std_name', '').strip()
        std_email = request.form.get('std_email', '').strip()

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Update student data in database
                    cursor.execute("""
                        UPDATE student_details 
                        SET std_name = %s, std_email = %s 
                        WHERE std_id = %s
                    """, (std_name, std_email, session['student_id']))
                    conn.commit()
                    flash('Profile updated successfully.', 'success')
                except Exception as e:
                    flash(f'Error: {str(e)}', 'error')
        
        return redirect(url_for('profile'))
    
    flash('Unauthorized access.', 'error')
    return redirect(url_for('login'))


# Password Reset
@app.route('/reset_password', methods=['POST'])
def reset_password():
    if 'user_type' in session and session['user_type'] == 'student':
        password = request.form.get('std_passwd', '').strip()
        confirm_password = request.form.get('confirm-password', '').strip()

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('profile'))

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Update the password in the database
                    cursor.execute("""
                        UPDATE student_details 
                        SET std_passwd = %s 
                        WHERE std_id = %s
                    """, (password, session['student_id']))
                    conn.commit()
                    flash('Password updated successfully.', 'success')
                except Exception as e:
                    flash(f'Error: {str(e)}', 'error')
        
        return redirect(url_for('profile'))
    
    flash('Unauthorized access.', 'error')
    return redirect(url_for('login'))

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


@app.route('/student/attendance/<int:student_id>')
def attendance(student_id):
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
    """, (student_id,student_id))
    session_details = cursor.fetchone()
    
    # You can add logic here to fetch student-specific attendance details
    return render_template('student/attendance.html',attendance=session_details)

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

# @app.route("/student/profile")
# def profile():
#     """Render the profile page."""
#     return render_template("/student/profile.html", student=student_data)

# profile updates
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


# Student dashboard route
@app.route('/student/dashboard/<int:student_id>')
def student_dashboard(student_id):
    if 'user_type' not in session or session['user_type'] != 'student' or session.get('student_id') != student_id:
        # If the user is not logged in or the session does not match the student ID
        flash('You must be logged in as a student to access the dashboard.', 'error')
        return redirect(url_for('login'))  # Redirect to login page if not logged in as a student
    # Fetch student-specific data if required using the student_id
    return render_template('student/dashboard.html', student_id=student_id)




# Admin dashboard 
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_type' not in session or session['user_type'] != 'admin':
        flash('You must be logged in as an admin to access this page.', 'error')
        return redirect(url_for('login'))  # Redirect to the login page if not admin
    
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
@app.route('/admin/session/<int:s_id>/attendance_view/pdf')
def generate_attendance_pdf(s_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get session details
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

    # Generate PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setTitle("Attendance Report")
    pdf.drawString(100, height - 100, f"Attendance Report for {session_details['course_name']}")
    pdf.drawString(100, height - 120, f"Date: {session_details['s_date']}")
    pdf.drawString(100, height - 140, f"Batch: {session_details['bat_name']}")
    pdf.drawString(100, height - 160, "Student Attendance:")

    # Add table headers
    pdf.drawString(100, height - 180, "Roll No")
    pdf.drawString(200, height - 180, "Name")
    pdf.drawString(300, height - 180, "Login Time")
    pdf.drawString(400, height - 180, "Logout Time")

    # Add student attendance data
    y_position = height - 200
    for student in students:
        pdf.drawString(100, y_position, student['std_rollno'])
        pdf.drawString(200, y_position, student['std_name'])
        pdf.drawString(300, y_position, str(student['login_time']) if student['login_time'] else "Absent")
        pdf.drawString(400, y_position, str(student['logout_time']) if student['logout_time'] else "Absent")
        y_position -= 20  # Move down for the next student

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="attendance_report.pdf", mimetype='application/pdf')


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


# courses
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

# admin students
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

#devices
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

#sessions
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

    # Include a link to generate the PDF for this session
    attendance_pdf_url = url_for('generate_attendance_pdf', s_id=s_id)

    return render_template(
        'admin/attendance_view.html', 
        session=session_details, 
        students=students,
        attendance_pdf_url=attendance_pdf_url
    )



if __name__ == '__main__':
    app.run(debug=True)
