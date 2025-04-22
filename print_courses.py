from gradescopeapi.classes.connection import GSConnection

connection = GSConnection()
import keyring
username = keyring.get_password('gradescope', 'username')
password = keyring.get_password('gradescope',   username)
connection.login(username, password)

courses = connection.account.get_courses()

for course in courses['instructor']:
    print(course, courses['instructor'][course].name)
