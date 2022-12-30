import json

import mariadb
import sys

from datetime import datetime, timedelta

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="root",
        password="Iha*2020",
        host="localhost",
        port=3306,
        database="gsg_std_reg_sys",
        plugin_dir="C:\\Program Files\\MariaDB 10.10\\lib\\plugin"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()


# Get Levels
def get_levels():
    cur.execute(f"""select level_id, level_name from levels;""")
    levels = cur.fetchall()
    return levels


# Add New Students
def add_std(student_name, dob, level_id, mobile_number, email):
    qry_add_cont = f"""insert into contacts (mobile_number, email)
                    values ('{mobile_number}', '{email}');"""

    cur.execute(qry_add_cont)
    cont_id = cur.lastrowid

    qry_add_std = f"""INSERT INTO students (student_name, dob, level_id, contact_id)
                    values ('{student_name}', '{dob}', {level_id}, {cont_id});"""
    cur.execute(qry_add_std)
    conn.commit()
    print("Student has been added")

# add_std('test2', 1/1/2000, 1, 123, 'mail@ma.il')


# Add New Course
def add_course(course_name, max_capacity, rate_per_hour, level_id):
    qry_add_course = f"""insert into courses (course_name, max_capacity, rate_per_hour, level_id)
                    values ('{course_name}', {max_capacity}, {rate_per_hour}, {level_id});"""
    cur.execute(qry_add_course)
    conn.commit()
    print("Course has been added")


# Create a course schedule
def course_schedule(day, course_id, start_time, duration):
    # check course interruption
    qry = f"""SELECT * FROM course_schedules
              JOIN courses ON course_schedules.course_id = courses.course_id
              WHERE day='{day}' AND courses.course_id={course_id} AND start_time <='{start_time}' 
              AND (date_add(start_time, interval {duration} hour)) >= '{start_time}'"""
    cur.execute(qry)
    count = cur.rowcount
    # print(count)
    if count > 0:
        print("that would make an interruption")
    else:
        qry_add_schedule = f"""insert into course_schedules (course_id, day, start_time, duration)
        values ({course_id}, '{day}', '{start_time}', {duration})"""
        cur.execute(qry_add_schedule)
        conn.commit()

# print(course_schedule('Saturday', 2, '12:00', 2))


# Get Student schedule
def student_schedule(student_id):
    cur.execute(f"""select * from students where student_id = {student_id}""")
    student_details = cur.fetchall()
    if student_details:
        print("student id:", student_details[0][0], " | ", "Student name:", student_details[0][1])
        print("---------------------------------------")
        cur.execute(f"""select c.course_name, cs.day, cs.start_time, cs.duration from enrollment_history e
                        left join courses c on c.course_id = e.course_id
                        right join students s on e.student_id = s.student_id
                        left join course_schedules cs on c.course_id = cs.course_id
                        where s.student_id = {student_id} """)
        student_schedule = cur.fetchall()
        if student_schedule: # [0] == None
            print("Course Name \t \t Day \t \t Start Time \t \t Duration")
            print("-----------------------------------------------------")
            for row in student_schedule:
                print(row[0], "\t \t", row[1], "\t \t", row[2], "\t \t", row[3])
                print("-----------------------------------------------------")
        else:
            print("no schedule courses for selected student")
    else:
        print("There is no such student")


def get_student_details(student_id):
    cur.execute(f"""select s.*, c.mobile_number, c.email, l.level_name from students s
                                        left join contacts c on s.contact_id = c.contact_id
                                        left join levels l on l.level_id = s.level_id where s.student_id = {student_id};""")
    students_list = cur.fetchall()
    students = {}
    for row in students_list:
        students.update({'student_id': row[0], 'student_name': row[1], 'contact_id': row[2],
                         'address_id': row[3], 'level_id': row[4], 'dob': row[5], 'mobile_number': row[6],
                         'email': row[7], 'level_name': row[8]})
    return students


def get_course_details(course_id):
    cur.execute(f"""select * from courses c where c.course_id = {course_id};""")
    courses_list = cur.fetchall()
    courses = {}
    for row in courses_list:
        courses.update({'course_id': row[0], 'level_id': row[1], 'course_name': row[2],
                        'max_cap': row[3], 'rate_hour': row[4]})
    return courses


def get_enrollment_history(course_id, student_id):
    cur.execute(f"""select * from enrollment_history eh
                    where course_id = {course_id} and student_id = {student_id};""")
    enrollment_history = cur.fetchall()
    enrollment = []
    for row in enrollment_history:
        enrollment.append({'enroll_id': row[0], 'student_id': row[1], 'course_id': row[2],
                         'enroll_date': row[3], 'total_hours': row[4], 'total': row[5]})
    return enrollment


def check_capacity(course_id):
    cur.execute(f"""select count(enroll_id) from enrollment_history eh
                        where course_id = {course_id};""")
    for row in cur.fetchall():
        total_enroll = row[0]

    cur.execute(f"""select max_capacity from courses c
                            where course_id = {course_id};""")
    for row in cur.fetchall():
        max_capacity = row[0]

    if total_enroll >= max_capacity:
        return False
    else:
        return True


def enroll(student_id, course_id):
    # Check if course has schedules
    qry_chk = f"""select * from course_schedules where course_id = {course_id}"""
    cur.execute(qry_chk)
    count = cur.rowcount
    thours = total_hours(course_id)
    rate_hour = get_course_details(course_id)["rate_hour"]
    total = thours * rate_hour
    # insert into enrollment history
    if count > 0:
        qry_enroll = f"""INSERT INTO enrollment_history (student_id, course_id, enroll_date, total_hours, total)
                            values ({student_id}, {course_id}, curdate(), {thours}, {total});"""
        cur.execute(qry_enroll)
        conn.commit()
        print("Enrollment Completed")
    else:
        print("Course has no schedules")


def total_hours(course_id):
    cur.execute(f"""select course_id, sum(duration) from course_schedules
                    where course_id = {course_id}""")
    thours = cur.fetchall()
    th = int(thours[0][1])
    return th
