from gradescopeapi.classes.connection import GSConnection
from gradescopeapi.classes.assignments import update_assignment_date
from gradescopeapi.classes.extensions import get_extensions, update_student_extension
from datetime import datetime, timedelta

# create connection and login
connection = GSConnection()
import keyring
username = keyring.get_password('gradescope', 'username')
password = keyring.get_password('gradescope',   username)
connection.login(username, password)

import argparse

# Usage:
# python grant_extension.py course_id "John Doe" HW2 "2025-04-21"

parser = argparse.ArgumentParser(description="Grant extension to a student")
parser.add_argument("course_id", type=str, help="Course ID")
parser.add_argument("name", type=str, help="Name of the student")
parser.add_argument("assignment", type=str, help="Name of the assignment (prefix)")
parser.add_argument("new_due_date", type=str, help="Extended due date for the assignment")
parser.add_argument("--late_due_date", type=str, help="Custom late due date of the assignment (optional -- defaults to 24 hours after new due date)")

args = parser.parse_args()
course_id = args.course_id
name = args.name
assignment_name = args.assignment
new_due_date = datetime.strptime(args.new_due_date, "%Y-%m-%d")
new_due_date = new_due_date.replace(hour=23, minute=59, second=59)

if args.late_due_date:
    late_due_date = datetime.strptime(args.late_due_date, "%Y-%m-%d")
    late_due_date = late_due_date.replace(hour=23, minute=59, second=59)
else:
    late_due_date = new_due_date + timedelta(days=1)

if assignment_name[0:2] != 'HW':
    raise ValueError("Assignment name must start with 'HW'")

matching = []
members = connection.account.get_course_users(course_id)
for member in members:
    if (member.full_name.find(name) != -1):
        matching.append(member)

if (len(matching) != 1):
    raise Exception(f'There must be exactly one match for the student name (found {len(matching)})')

print(matching[0])

# Prompt for confirmation
print(f"Granting extension to {matching[0].full_name}")
print(f"Assignment: {assignment_name}")
print(f"New due date: {new_due_date}")
print(f"Late due date: {late_due_date}")
confirm = input("Do you want to proceed? (y/n): ")
if confirm.lower() != 'y':
    print("Operation cancelled.")
    exit()

assignments = connection.account.get_assignments(course_id)
for assignment in assignments:
    n = assignment.name
    if n[0:len(assignment_name)] != assignment_name: continue
    if n.find('written') != -1:
        print(f"Skipping written assignment {assignment.name}")
        continue

    extensions = get_extensions(connection.session, course_id, assignment.assignment_id)

    print("Updating extension for assignment:", assignment.name)

    result = update_student_extension(
        connection.session,
        course_id,
        assignment.assignment_id,
        matching[0].gradebook_user_id,
        assignment.release_date,
        new_due_date,
        late_due_date,
    )
    if not result: print(f"Failed!")
