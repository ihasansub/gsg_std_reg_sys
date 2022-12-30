# This is a sample project for a students registration system
# import requests
# import json
from datetime import datetime
import functions
import inquirer

while True:
    print("""
    1/ Register New Student \t \t 2/ Enroll Course
    3/ Create New Course \t \t \t 4/ Create Course Schedule
    5/ Display Student Schedule \t 6/ break""")

    action = input("Choose Action (type the number only) ")
    # 1/ Register New Student
    if action == "1":
        student_name = input("Enter Student Name: ")
        dob = input('Enter a date formatted as yyyy-mm-dd: ')
        for row in functions.get_levels():
            print(row)
        level_id = int(input("Enter level number form list above: "))
        mobile_number = input("Enter Mobile Number: ")
        email = input("Enter Email: ")

        functions.add_std(student_name, dob, level_id, mobile_number, email)

    # 2/ Enroll Course
    elif action == "2":
        student_id = int(input("Enter Student ID: "))
        course_id = int(input("Enter Course ID: "))
        std_details = functions.get_student_details(student_id)
        course_details = functions.get_course_details(course_id)
        if std_details["level_id"] == course_details["level_id"]:
            taken = functions.get_enrollment_history(course_id, student_id)
            if taken == []:
                if functions.check_capacity(course_id):
                    functions.enroll(student_id, course_id)
                else:
                    print("Student Can't Enroll This Course! Capacity is FULL.")
            else:
                print("Student Can't Enroll This Course! He took it previously.")
        else:
            print("Student Can't Enroll This Course! It is in a higher level.")

    # 3/ Create New Course
    elif action == "3":
        # course_id = input("Enter course code: ")
        course_name = input("Enter course name: ")
        max_capacity = input("Enter max capacity: ")
        rate_per_hour = input("Enter rate/hour: ")
        for row in functions.get_levels():
            print(row)
        level_id = int(input("Enter level number form list above: "))
        functions.add_course(course_name, max_capacity, rate_per_hour, level_id)

    # 4/ Create Course Schedule
    elif action == "4":
        # questions = [
        #     inquirer.List('day',
        #                   message="Choose a day",
        #                   choices=['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        #                   ),
        # ]
        # answers = inquirer.prompt(questions)
        # day = answers['day']
        day = input("Enter Day")
        course_id = int(input("Enter course code: "))
        start_time = input("Enter start time: ")
        duration = int(input("Enter course duration: "))

        functions.course_schedule(day, course_id, start_time, duration)

    # 5/ Display Student Schedule
    elif action == "5":
        student_id = input("Enter Student ID: ")
        functions.student_schedule(student_id)

    elif action == "6":
        print("Have a nice day!")
        break

    else:
        print("There is no action listed with that number!")
