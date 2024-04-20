import csv
import mysql.connector

# Fancy database stuff
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="testdatabase"
)


def create_table():
    cursor = db.cursor()

    # create the table
    cursor.execute("CREATE TABLE Cars (id INT PRIMARY KEY AUTO_INCREMENT, "
                   "mpg FLOAT, "
                   "cylinders FLOAT, "
                   "engine FLOAT, "
                   "horsepower FLOAT, "
                   "weight FLOAT, "
                   "acceleration FLOAT, "
                   "year FLOAT, "
                   "origin VARCHAR(50), "
                   "name VARCHAR(50))")

    # Reading the file, skip the header, use csv.reader to read through it.
    # For each element in each row, if the element is nan, turn it to zero.
    # Try to convert the element to float, otherwise keep it as a string
    with open("Car performance data.csv", "r") as file:
        next(file)
        f = csv.reader(file)
        for x in f:
            for y in range(len(x)):
                if x[y] == 'nan':
                    x[y] = 0
                try:
                    x[y] = float(x[y])
                except:
                    continue
            query = "INSERT INTO Cars (mpg, cylinders, engine, horsepower, weight, acceleration, year, origin, name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8])
            cursor.execute(query, values)

    print("Table created!\n")
    db.commit()
    cursor.close()


def drop_table():
    cursor = db.cursor()
    cursor.execute("DROP TABLE Cars")
    print("\nTable destroyed!\n")
    db.commit()
    cursor.close()


def reset_table():
    confirm = input("Are you SURE you want to reset the table? Type CONFIRM to confirm or anything else to exit:\n")
    if confirm == "CONFIRM":
        confirm = input("Type I AM SURE to reset the table or anything else to exit. This is your last chance.\n")
        if confirm == "I AM SURE":
            print("\nTable resetting.")
            drop_table()
            create_table()


def check_exit(term):
    if term == "x":
        print("Going back to menu...")
        return True
    return False


def print_table(mode, rows = None):
    # Case for print full table
    if not rows:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Cars")
        rows = cursor.fetchall()
        cursor.close()

    # Cases for print full table, print found rows, and print one row, respectively
    match mode:
        case 1:
            i = 0
            for x in rows:
                for y in x:
                    print(headers[i].title() + ":", y, end="   ")
                    i += 1
                i = 0
                print()
        case 2:
            i = 0
            print("We found these cars in the table.")
            for x in rows:
                for y in x:
                    print(headers[i].title() + ":", y, end="   ")
                    i += 1
                i = 0
                print()
        case 3:
            i = 0
            for x in rows:
                for y in x:
                    print(headers[i].title() + ":", y, end="   ")
                    i += 1


# Create list of headers for printing
def get_headers():
    cursor = db.cursor()
    cursor.execute("SHOW COLUMNS FROM Cars")
    headersList = []

    for x in cursor:
        headersList.append(x[0])
    cursor.close()
    return headersList

# Main menu. Continue loop until exited.
def get_choice():
    choice = "1"
    while choice in {"1", "2", "3", "4", "5", "6"}:
        choice = input("\nInput 1 to view the full table, 2 to search for a term, 3 to change a term, 4 to add an item, 5 to delete an item, 6 to completely reset the table, or anything else to quit.\n")

        match choice:
            case "1":
                print_table(1)
            case "2":
                find_value()
            case "3":
                change_value()
            case "4":
                add_item()
            case "5":
                delete_item()
            case "6":
                reset_table()

# First get column parameter, make sure it is valid (in headers)
# Then get search term. If it's not numeric for the first 7 columns
# immediately return nothing.
def find_value():
    while True:
        cursor = db.cursor()

        print("Choose a parameter from the following list to search under: [OR X TO GO BACK TO MENU]")
        for x in headers:
            print(x, end=" ")

        para = (input("\n")).lower()
        if check_exit(para):
            cursor.close()
            return

        while para not in headers:
            para = (input("Please choose one of the listed choices. [OR X TO GO BACK TO MENU]\n")).lower()
            if check_exit(para):
                cursor.close()
                return

        term = input("What value under '" + para + "' would you like to search for? [OR X TO GO BACK TO MENU]\n")
        if check_exit(term):
            cursor.close()
            return

        if headers.index(para) < 8:
            try:
                float(term)
            except:
                print("We couldn't find any cars that match this description.")
                retry = input("Enter 1 to retry or any other character to quit.\n")
                cursor.close()

                if retry == "1":
                    continue
                return

        query = "SELECT * FROM Cars WHERE {} = %s".format(para)
        values = (term,)
        cursor.execute(query, values)

        rows = cursor.fetchall()
        if not rows:
            print("We couldn't find any cars that match this description.")
            retry = input("Enter 1 to retry or any other character to quit.\n")
            cursor.close()

            if retry == "1":
                continue
        else:
            print_table(2, rows)
        cursor.close()
        break

# Make sure row input is valid (number and contained in the table)
# If not line, meaning nothing is found, then it's not valid
# Then take column parameter being changed, and then term value
# assuming it is valid
def change_value():
    while True:
        row = input("Which item would you like to change (by ID)? [OR X TO GO BACK TO MENU]\n")
        if check_exit(row):
            return
        if row.isdigit():
            int(row)

            cursor = db.cursor()
            query = "SELECT * FROM Cars WHERE id = %s"
            values = (row,)
            cursor.execute(query, values)
            line = cursor.fetchall()
            cursor.close()

            if line:
                print_table(3, line)
            else:
                print("That ID is out of range or has been deleted. Please select a valid ID.\nWe recommend you check the full table to see what is available.")
                continue

            choice = input("\nIs this the right item? Enter 1 for yes, 2 for no and try again, or anything else to exit.\n")

            if choice == "1":
                break
            elif choice != "2":
                return

        else:
            print("We couldn't find an item with that ID. Please try again")

    while True:
        print("Choose a parameter from the following list to change: [OR X TO GO BACK TO MENU]")
        for x in headers[1:]:
            print(x, end=" ")

        col = (input("\n")).lower()
        if check_exit(col):
            return

        while col not in headers[1:]:
            col = input("Please choose one of the listed choices [OR X TO GO BACK TO MENU]\n")
            if check_exit(col):
                return

        value = (input("What would you like to change " + col + " to? [OR X TO GO BACK TO MENU]\n")).lower()
        if check_exit(value):
            return

        if col != ("origin" and "name"):
            try:
                value = float(value)
            except:
                print("This is not a valid entry. Please input a numeric value for this parameter.")
                continue
        break

    cursor = db.cursor()
    query = "UPDATE Cars SET {} = %s WHERE id = %s".format(col)
    values = (value, row)
    cursor.execute(query, values)
    query = "SELECT * FROM Cars WHERE id = %s"
    values = (row,)
    cursor.execute(query, values)
    line = cursor.fetchall()
    cursor.close()

    print("The entry has been modified:")
    print_table(3, line)
    print()

    db.commit()

# Pretty simple. Just loop for each header (excluding id)
# and append the entered value to a list. Then use the list
# to create the row
def add_item():
    print("Enter the corresponding data for each term. At any time you can enter X to go back to the menu.")
    items = []

    for x in headers[1:]:
        item = input(x + ": ")
        if check_exit(item):
            return

        while True:
            if headers.index(x) < 8:
                try:
                    float(item)
                    break
                except:
                    print("Invalid input. Please enter a number for this value.")
                    item = input(x + ": ")
            else:
                break
        items.append(item)

    cursor = db.cursor()
    query = "INSERT INTO Cars (mpg, cylinders, engine, horsepower, weight, acceleration, year, origin, name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (items[0], items[1], items[2], items[3], items[4], items[5], items[6], items[7], items[8])
    cursor.execute(query, values)
    cursor.execute("SELECT * FROM Cars ORDER BY id DESC LIMIT 1")
    row = cursor.fetchall()
    print("Row added:")
    print_table(3, row)
    cursor.close()

    db.commit()

# Just have to confirm that the entered ID is valid
# and then confirm deletion
def delete_item():
    while True:
        row = input("Which item would you like to delete (by ID)? [OR X TO GO BACK TO MENU]\n")
        if check_exit(row):
            return

        if row.isdigit():
            int(row)

            cursor = db.cursor()
            query = "SELECT * FROM Cars WHERE id = %s"
            term = (row,)
            cursor.execute(query, term)
            line = cursor.fetchall()
            cursor.close()

            if line:
                print_table(3, line)
            else:
                print(
                    "That ID is out of range or has been deleted. Please select a valid ID.\nWe recommend you check the full table to see what is available.")
                continue

            choice = input("\nIs this the right item? Enter 1 for yes, 2 for no and try again, or anything else to exit\n")
            if check_exit(choice):
                return

            if choice == "1":
                break
            elif choice != "2":
                return

        else:
            print("We couldn't find an item with that ID. Please try again")

    choice = input("Are you sure you want to delete this item? Type 1 to confirm or anything else to exit\n")

    if choice == "1":
        cursor = db.cursor()
        query = "DELETE FROM Cars WHERE id = %s"
        values = (row,)
        cursor.execute(query, values)
        cursor.close()

    print("Row deleted!")

    db.commit()


###########################################
            # Main Function
###########################################

try:
    create_table()
except:
    print("Table already created.")
headers = get_headers()
get_choice()
