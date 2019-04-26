import sqlite3
import getpass as gp
from caster import Core

def password_validity(password):
    # Check that entered password is valid with a set of rules as lambda fxns
    rules = [
            lambda s: not s.isalnum(), # must have one symbol
            lambda s: any(x.isupper() for x in s),  # must have at least one uppercase
            lambda s: any(x.islower() for x in s),  # must have at least one lowercase
            lambda s: any(x.isdigit() for x in s),  # must have at least one number
            lambda s: len(s) >= 8                   # must be at least 8 characters
            ]
    # return true if all rules pass, and false otherwise
    if all(rule(password) for rule in rules):
        return True
    else:
        return False

def create_new_user():
    # New user code
    print("Creating new user...")
    user = ""
    while(True):
        user = input("Enter a username: ")
        if (user.isalnum()):
            break;
        else:
            print("Please enter a username with only letters and numbers.")
    password = ""
    while(True):
        password = gp.getpass("Enter a password (must contain at least a capital and lowercase letter, a number, a symbol, and 8 characters): ")
        if (password_validity(password)):
            check_pass = gp.getpass("Re-enter your password: ")
            if (check_pass == password):
                break;
            else:
                print("Passwords did not match!")
        else:
            print("Password must contain at least one capital letter, one lowercase letter, one number, one symbol, and be at least 8 characters!")
    if (user != "" and password != ""):
        add_user(user, password)
        return (user, password)
    else:
        print("Failed to create user " + user + "!")
        return ("", "")

def verify_existing_user(username, password):
    # Check that user/password exists in db
    print("Verifying username/password...")
    connection = sqlite3.connect('src/usr/userbase.sqlite3')
    cursor = connection.execute("SELECT * FROM users WHERE username == \"" + username + "\";")
    user = cursor.fetchone()
    if (user[1] == password):
        print("Credentials verified.")
        return True
    else:
        print("Username or Password is incorrect.")
        return False

def add_user(username, password, tutorialized=0, fullscreen=1):
    # Create a new user with default values and user/pass combo
    print("Creating profile...")
    connection = sqlite3.connect('src/usr/userbase.sqlite3')
    user = (username, password, tutorialized, fullscreen)
    connection.execute("INSERT INTO users VALUES (?, ?, ?, ?);", user)
    connection.commit()
    connection.close()

def get_user_fs_setting(username):
    # Return the fullscreen setting for the associated user
    print("Fetching fullscreen setting...")
    connection = sqlite3.connect('src/usr/userbase.sqlite3')
    cursor = connection.execute("SELECT * FROM users WHERE username == \"" + username + "\";")
    user = cursor.fetchone()
    connection.commit()
    connection.close()
    return user[3]

def get_user_tut_setting(username):
    # Return whether or not user has been tutorialized
    print("Checking tutorial status...")
    connection = sqlite3.connect('src/usr/userbase.sqlite3')
    cursor = connection.execute("SELECT * FROM users WHERE username == \"" + username + "\";")
    user = cursor.fetchone()
    connection.commit()
    connection.close()
    return user[2]

if __name__ == "__main__":
    print("Welcome to Caster 2D!")
    usrnm = ""
    while(True):
        pswd = ""
        answer = input("Do you have an account? y/n: ")
        answer = answer.lower()
        if (answer == "y" or answer == "yes"):
            usrnm = input("Username: ")
            pswd = gp.getpass()
        else:
            newusr = create_new_user()
            usrnm = newusr[0]
            pswd = newusr[1]
        if(verify_existing_user(usrnm, pswd)):
            break
        else:
            print("Please enter an appropriate username/password, or create a new account.")
    fs = get_user_fs_setting(usrnm)
    ttlz = get_user_tut_setting(usrnm)
    main = Core(usrnm, fs, ttlz)
    main.run()
    if main.is_fullscreen:
        set_user_fs_setting(usrnm, 1)
    else:
        set_user_fs_setting(usrnm, 0)
    if main.tutorialized:
        set_user_tut_setting(usrnm, 1)
    else:
        set_user_tut_setting(usrnm, 0)
