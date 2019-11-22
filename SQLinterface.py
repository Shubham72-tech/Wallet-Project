import sqlite3
import os
from sqlite3 import Error
import getch
 
 
def create_connection(DB_file):

    conn = None
    try:
        conn = sqlite3.connect(DB_file)
    except Error as e:
        print(e)
 
    return conn
 
def clearScr():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def select_all(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)
    
    print("\n\nPress Any key to continue")
    getch.getch()
 
 
def select_user(conn):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    clearScr()
    acc_id = int(input("Enter account number : "))
    if verifyExists(acc_id)==0:
        print("User Does not exists")
    else:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE acc_id=?", (acc_id,))
    
        rows = cur.fetchall()
    
        for row in rows:
            if row[2]=='s':
                acc_type="Savings"
            if row[2]=='c':
                acc_type="Current"
            print("Account Number:", row[0])
            print("Account Holder Name:", row[1])
            print("Account Type:", acc_type)
            print("Account Balance:", row[3])
    getch.getch()
 
def verifyExists(acc_id):
    conn = create_connection("SQL_db.db")
    cur = conn.cursor()
    sql_command="SELECT EXISTS(SELECT 1 FROM users WHERE acc_id=?)"
    user_data=(acc_id,)
    cur.execute(sql_command,user_data)
    val=cur.fetchall()
    val=val[0]
    tval=val
    return tval[0]


def new_user(conn):

    clearScr()
    acc_id = int(input("Enter Account Number : "))
    val=verifyExists(acc_id)
    if val == 0:
        cur = conn.cursor()
        acc_name = input("Enter User Name : ")
        acc_type = input("Enter Account Type (savings [s] / current [c]) : ")
        acc_balance = float(input("Enter Initial Deposit: "))

        user_data=(acc_id,acc_name,acc_type,acc_balance)

        sql_command="INSERT INTO users (`acc_id`, `acc_name`, `acc_type`, `acc_balance`) VALUES (?,?,?,?);"

        cur.execute(sql_command,user_data)
        conn.commit()
        print("User Created Successfully ")
    else:
        print("User already exists")
        getch.getch()

def deposit(conn):

    cur = conn.cursor()
    clearScr()
    acc_id = int(input("Enter Account Number: "))
    val = verifyExists(acc_id)
    if val == 0:
        print("User does not exists")
    else:
        amount = float(input("Enter deposit amount: "))

        user_data = (amount, acc_id)
        sql_command = "UPDATE users SET acc_balance=acc_balance+? WHERE acc_id=?"
        cur.execute(sql_command,user_data)
        conn.commit()
        print("Deposit added successfully.  press any key to continue")
        getch.getch()

def withdrawal(conn):

    cur = conn.cursor()
    clearScr()
    acc_id = int(input("Enter Account Number: "))
    val = verifyExists(acc_id)
    if val == 0:
        print("User does not exists")
    else:
        amount = float(input("Enter withdrawal amount: "))

        user_data = (amount, acc_id)
        sql_check="SELECT acc_balance FROM users WHERE acc_id=?"
        cur.execute(sql_check,(acc_id,))
        check=cur.fetchall()
        check=check[0]
        tcheck=check
        if tcheck[0]>= amount:
            sql_command = "UPDATE users SET acc_balance=acc_balance-? WHERE acc_id=?"
            cur.execute(sql_command,user_data)
            conn.commit()
            print("Withdrawn Successfully.  press any key to continue")
            getch.getch()
        else:
            print("Balance Too low")
            getch.getch()

def deleteUser(conn):
    
    acc_id = int(input("Enter account number : "))
    if verifyExists(acc_id)==0:
        print("User Does not exists")
    else:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE acc_id=?", (acc_id,))
        rows = cur.fetchall()
        for row in rows:
            print(" Are you Sure You want to Delete(y/n) : ", row[1])
        confirmation=input()
        if confirmation == 'y':
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE acc_id=?", (acc_id,))
            conn.commit()
            print("User ID Deleted Successfully")
        elif confirmation == 'n':
            clearScr()
            main()
        

    getch.getch()
"""
def main():
    database = "SQL_db.db"
 
    # create a database connection
    conn = create_connection(database)
    with conn:
        print("1. New account    ")
        print("2. Account info   ")
        print("3. All accounts   ")
        print("4. New Deposit    ")
        print("5. New Withdrawal ")
        print("6. Delete user    ")
        print("7. exit           ")
        Input = getch.getch()
        if Input == '1':
            new_user(conn)
        elif Input == '2':
            select_user(conn)
        elif Input == '3':
            select_all(conn)
        elif Input == '4':
            deposit(conn)
        elif Input == '5':
            withdrawal(conn)
        elif Input == '6':
            deleteUser(conn)
        elif Input == '7':
            exit()
        else:
            print("Invalid Input")
            
        clearScr()
        main()

 
 
if __name__ == '__main__':
    main()
    """