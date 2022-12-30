# import json
from flask import Flask, render_template, request, jsonify
import simplejson
import functions
import datetime
import jinja2

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("home.html")


@app.route("/courses.html")
def courses():
    functions.cur.execute(f"""select c.*, l.level_name from courses c
left join levels l on c.level_id = l.level_id;""")
    courses_list = functions.cur.fetchall()
    courses = []
    for row in courses_list:
        courses.append({'course_id': row[0], 'level_id': row[1], 'course_name': row[2],
                        'max_capacity': row[3], 'rate_per_hour': row[4], 'level_name': row[5]})

    cour = {}
    cour.update({'data': courses})
    resp = simplejson.dumps(cour)
    resp = simplejson.loads(resp)
    return render_template("courses.html", **resp)


@app.route("/students.html")
def students():
    functions.cur.execute(f"""select s.*, c.mobile_number, c.email, l.level_name from students s
                            left join contacts c on s.contact_id = c.contact_id
                            left join levels l on l.level_id = s.level_id;""")
    students_list = functions.cur.fetchall()
    students = []
    for row in students_list:
        students.append({'student_id': row[0], 'student_name': row[1], 'contact_id': row[2],
                        'address_id': row[3], 'level_id': row[4], 'dob': str(row[5]), 'mobile_number':row[6],
                         'email': row[7], 'level_name': row[8]})

    std = {}
    std.update({'data': students})
    resp = simplejson.dumps(std)
    resp = simplejson.loads(resp)
    return render_template("students.html", **resp)


@app.route("/courses_schedules.html")
def course_schedules():
    functions.cur.execute(f"""select cs.*, c.course_name from course_schedules cs
                        left join courses c on c.course_id = cs.course_id
                        order by c.course_id;""")
    schedules_list = functions.cur.fetchall()
    schedules = []
    for row in schedules_list:
        schedules.append({'course_id': row[1], 'day': row[2], 'start_time': str(row[4]),
                        'duration': row[3], 'course_name': row[5], 'end_time': str(row[4] + datetime.timedelta(hours=row[3]))})

    course_sch = {}
    course_sch.update({'data': schedules})
    resp = simplejson.dumps(course_sch)
    resp = simplejson.loads(resp)
    return render_template("courses_schedules.html", **resp)


@app.route("/get_student_details/")
def get_student_details():
    auth = request.headers.get("stdapi")
    if auth == "123456":
        std_id = request.args.get('std_id')
        functions.cur.execute(f"""select s.*, c.mobile_number, c.email, l.level_name from students s
                                    left join contacts c on s.contact_id = c.contact_id
                                    left join levels l on l.level_id = s.level_id where s.student_id = {std_id};""")
        students_list = functions.cur.fetchall()
        students = {}
        for row in students_list:
            students.update({'student_id': row[0], 'student_name': row[1], 'contact_id': row[2],
                             'address_id': row[3], 'level_id': row[4], 'dob': row[5], 'mobile_number': row[6],
                             'email': row[7], 'level_name': row[8]})
        return jsonify(students)
    else:
        reply = {"message": "Auth Error"}
        return jsonify(reply)


app.run(debug=True)
