from gradescopeapi.classes.connection import GSConnection
from gradescopeapi.classes.assignments import update_assignment_date
from datetime import datetime, timedelta

import argparse

# Usage:
# python set_due_date.py course_id HW2 "2025-04-21" "2025-04-27"

parser = argparse.ArgumentParser(description="Grant extension to a student")

parser.add_argument("course_id", type=str, help="Course ID")
parser.add_argument("assignment", type=str, help="Name of the assignment (prefix)")
parser.add_argument("release_date", type=str, help="Release date for the assignment")
parser.add_argument("due_date", type=str, help="Due date for the assignment")
parser.add_argument("--late_due_date", type=str, help="Custom late due date of the assignment (optional -- defaults to 24 hours after new due date)")

args = parser.parse_args()
course_id = args.course_id
assignment_name = args.assignment
release_date = datetime.strptime(args.release_date, "%Y-%m-%d")
release_date = release_date.replace(hour=0, minute=0, second=0)

due_date = datetime.strptime(args.due_date, "%Y-%m-%d")
due_date = due_date.replace(hour=23, minute=59, second=59)

if args.late_due_date:
    late_due_date = datetime.strptime(args.late_due_date, "%Y-%m-%d")
    late_due_date = late_due_date.replace(hour=23, minute=59, second=59)
else:
    late_due_date = due_date + timedelta(days=1)

if assignment_name[0:2] != 'HW':
    raise ValueError("Assignment name must start with 'HW'")

# create connection and login
connection = GSConnection()
import keyring
username = keyring.get_password('gradescope', 'username')
password = keyring.get_password('gradescope',   username)

connection.login(username, password)

assignments = connection.account.get_assignments(course_id)
for assignment in assignments:
    n = assignment.name
    if n[0:len(assignment_name)] != assignment_name: continue

    print("Setting due date for assignment:", assignment.name)
    result = update_assignment_date(
        connection.session,
        course_id,
        assignment.assignment_id,
        release_date,
        due_date,
        late_due_date)
    if not result: print(f"Failed!")

    # result = update_student_extension(
    #     connection.session,
    #     course_id,
    #     assignment.assignment_id,
    #     matching[0].user_id,
    #     assignment.release_date,
    #     new_due_date,
    #     late_due_date,
    # )
    # if not result: print(f"Failed!")
