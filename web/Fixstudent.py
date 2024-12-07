# login time
# logout time

# get  attendance

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

