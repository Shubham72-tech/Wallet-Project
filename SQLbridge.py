import sqlite3
import os
from sqlite3 import Error
import getpass
import hashlib

#hash password before passing
def hashpass(password):
    hashed = hashlib.sha224(password.encode('utf-8')).hexdigest()
    return hashed

#Connect to Database when calling function
def create_connection(DB_file):

    conn = None
    try:
        conn = sqlite3.connect(DB_file)
    except Error as e:
        print(e)
 
    return conn
 
 #Simple Clear Screen command that works on both windows and linux
def clearScr():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

#Request User info From Database
def select_user_data(conn,username,password):

    clearScr()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE username=? AND password=?", (username,password,))

    rows = cur.fetchall()

    for row in rows:
        print("Account Holder Name:", row[1])
        print("Account username:", row[2])
        print("Account Password: ********")
        print("Account Balance:", row[4])
    input("press Enter to continue")
    userMenu(conn,username,password)

#delete user from admin
def admin_deleteuser(conn,username,password):
    clearScr()
    logo()
    print("\n")
    User = input("Enter username for user to delete: ")
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE username=?", (User,))
    rows = cur.fetchall()
    for row in rows:
        print(" Are you Sure You want to Delete(y/n) : ", row[1])
        confirmation=input()
        if confirmation == 'y':
            cur = conn.cursor()
            cur.execute("DELETE FROM user WHERE username=?", (User,))
            conn.commit()
            print("User ID Deleted Successfully")
        elif confirmation == 'n':
            clearScr()
        input("\nPress enter to continue")
        adminMenu()


#show all users to admin
def admin_allusers(conn,username,password):
    clearScr()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user ")
    rows = cur.fetchall()
    logo()
    print("\n----------------All Users----------------\n")
    print("|ID   |Name                |UserName            |Balance \n")
    for Id,name,username,password,balance in rows:
        print("|{:<5}|{:<20}|{:<20}|{:<8}|".format(Id,name,username,balance))
    print("\n")


#Show all transactions to admin
def admin_alltransactions(conn,username,password):
    clearScr()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions")
    rows = cur.fetchall()
    logo()
    print("\n----------------All Transactions----------------\n")
    print("|ID   |amount  |Source              |Destination         |Timestamp \n")
    for Id,amount,source,destination,timestamp in rows:
        print("|{:<5}|{:<8}|{:<20}|{:<20}|{}".format(Id,amount,source,destination,timestamp))
    print("\n")


#Allow a deposit in account
def Account_deposit(conn,username,password):
    
    clearScr()
    deposit_amount = input("\n\nEnter amount to deposit:  ")
    validate = getpass.getpass()
    validate = hashlib.sha224(validate.encode()).hexdigest()
    if validate==password:
        cur = conn.cursor()
        user_data = (deposit_amount,username,password)
        sql_command = "UPDATE user SET balance=balance+? WHERE username=? AND password=?"
        cur.execute(sql_command,user_data)
        conn.commit()
        print("Deposit of "+deposit_amount+" added Successfully")
        add_log(conn,'deposit - in',username,deposit_amount)
        input("Press enter to continue")
    else:
        print("Incorrect transaction password")


#Requests login info and validate
def login(conn):
    clearScr()
    username = input("\nEnter Username: ")
    password = getpass.getpass()
    password = hashpass(password)
    if validate_user(conn,username,password) == 1:
        #stuff
        print("valid user")
        clearScr()
        userMenu(conn,username,password)
    elif validate_user(conn,username,password) == 0:
        print("incorrect password")
    else:
        print("User Does not Exist")

#validate if user exist and password matches
def validate_user(conn,username,password):
    
    cur = conn.cursor()
    #username verify exist
    sql_command="SELECT EXISTS(SELECT 1 FROM user WHERE username=?)"
    user_data=(username,)
    cur.execute(sql_command,user_data)
    userverify=cur.fetchall()
    userverify=userverify[0]
    userverify=userverify[0]
    #password match with usernamee verify
    sql_command_pass="SELECT EXISTS(SELECT 1 FROM user WHERE username=? AND password=?)"
    user_data_withpass=(username,password,)
    cur.execute(sql_command_pass,user_data_withpass)
    passverify=cur.fetchall()
    passverify=passverify[0]
    passverify=passverify[0]
    if userverify == 1 & passverify == 1:
        return(1)
    elif userverify == 1 & passverify == 0:
        return(2)
    else:
        return(0)

#Withdraw from account
def Account_withdrawal(conn,username,password):
    
    clearScr()
    withdrawal_amount = float(input("\n\nEnter amount to withdraw:  "))
    validate = getpass.getpass()
    validate = hashlib.sha224(validate.encode()).hexdigest()
    if validate==password:
        cur=conn.cursor()
        validate_minimum_balance = "SELECT balance FROM user WHERE username = ? AND password = ?"
        validation_data = (username,password)
        cur.execute(validate_minimum_balance,validation_data)
        verification=cur.fetchone()

        if verification[0] > withdrawal_amount:
            cur=conn.cursor()
            user_data = (withdrawal_amount,username,password)
            sql_command = sql_command = "UPDATE user SET balance=balance-? WHERE username=? AND password=?"
            cur.execute(sql_command,user_data)
            conn.commit()
            print("Withdrawal of "+str(withdrawal_amount)+" is Successful")
            add_log(conn,username,'withdrawal - out',withdrawal_amount)
            input("press enter to continue")
        else:
            print("Balance too low")
            input("press enter to continue")
    else:
        print("Incorrect transaction password")
        input("press enter to continue")

#intra wallet transfer
def transfer_internal(conn,username,password):
    clearScr()
    payee = input("Enter username of the payee: ")
    withdrawal_amount = float(input("\n\nEnter amount to transfer:  "))
    validate = getpass.getpass()
    validate = hashlib.sha224(validate.encode()).hexdigest()
    if validate==password:#check password
        cur=conn.cursor()
        #check if balance available
        validate_minimum_balance = "SELECT balance FROM user WHERE username = ? AND password = ?"
        validation_data = (username,password)
        cur.execute(validate_minimum_balance,validation_data)
        verification=cur.fetchone()
        cur=conn.cursor()
        #check if payee exists
        payee_validation = "SELECT EXISTS(SELECT 1 FROM user WHERE username=?)"
        payee_data = (payee,)
        cur.execute(payee_validation,payee_data)
        payee_verify=cur.fetchall()
        payee_verify=payee_verify[0]
        payee_verify=payee_verify[0]
        if payee_verify == 1:
            if verification[0] > withdrawal_amount:
                cur=conn.cursor()
                user_data = (withdrawal_amount,username,password)
                sql_command = sql_command = "UPDATE user SET balance=balance-? WHERE username=? AND password=?"
                cur.execute(sql_command,user_data)
                conn.commit()
                cur=conn.cursor()
                user_data = (withdrawal_amount,payee)
                sql_command = sql_command = "UPDATE user SET balance=balance+? WHERE username=?"
                cur.execute(sql_command,user_data)
                conn.commit()
                print("Transfer of "+str(withdrawal_amount)+" is Successful to user "+payee)
                add_log(conn,username,payee,withdrawal_amount)
                input("press enter to continue")
            else:
                print("Balance too low")
                input("press enter to continue")
        else:
            print("payee does not exist")
            input("press enter to continue")
    else:
        print("Incorrect transaction password")
        input("press enter to continue")

#Transaction command
def add_log(conn,sender,receiver,amount):

    cur=conn.cursor()
    sql_command="INSERT INTO transactions ('amount','source','destination') values (?,?,?)"
    user_data=(amount,sender,receiver)
    cur.execute(sql_command,user_data)    
    conn.commit()

#New user registration
def newRegistration(conn):
    clearScr()
    logo()
    username = input("Enter username : ")
    password = getpass.getpass()
    password = hashpass(password)
    name = input("Enter Full Name: ")
    val = validate_user(conn,username,password)
    if val != 1:
        cur = conn.cursor()
        
        user_data=(name,username,password,0)

        sql_command="INSERT INTO user (`name`, `username`, `password`, `balance`) VALUES (?,?,?,?);"

        cur.execute(sql_command,user_data)
        conn.commit()
        print("User Created Successfully ")
    else:
        print("User already exists")
#Admin user check
def admin_login(conn,username,password):
    print("stuff")

#Open user specific log
def view_log_user(conn,username,password):
    clearScr()
    logo()
    cur=conn.cursor()
    SQL_query = "SELECT * FROM transactions WHERE source = ? OR destination = ?"
    Query_data = (username,username)
    cur.execute(SQL_query,Query_data)
    log_list=cur.fetchall()
    #print(log_list)
    print("|ID   |Amnt     |Source              |Destination         |Timestamp|\n")
    for i0,i1,i2,i3,i4 in log_list:
        print("|{:<5}|{:<9}|{:<20}|{:<20}|{}|".format(i0,i1,i2,i3,i4))
    print("\n")
    input("press enter to continue")


#main of the code
def main():
    clearScr()
    logo()
    print("\n1. login")
    print("\n2. Create New User")
    print("\n3. Admin Console")
    print("\n4. exit")

    Choice = input("\n\nEnter An option: ")
    if Choice == '1':
        login(conn)
    elif Choice == '2':
        newRegistration(conn)
    elif Choice == '3':

        adminMenu()
    elif Choice == '4':
        exit()
    else:
        print("Invalid input")
    input("press enter to continue")
    main()

#submenu for admin
def adminMenu():
    clearScr()
    logo()
    print("----------------------------")
    print("---------ADMIN MENU---------")
    print("----------------------------\n")
    print("1. view all users")
    print("2. view full transaction log")
    print("3. Delete User")
    print("4. Exit")
    Choice = input("\nEnter an option:--> ")
    if Choice == '1':
        admin_allusers(conn,username,password)
    elif Choice == '2':
        admin_alltransactions(conn,username,password)
    elif Choice == '3':
        admin_deleteuser(conn,username,password)
    elif Choice == '4':
        exit()
    else:
        print("Invalid input")
    print("\n")
    input("press enter to continue")
    adminMenu()

#submenu for user
def userMenu(conn,username,password):
    clearScr()
    logo()
    print("---------------------------")
    print("---------USER MENU---------")
    print("---------------------------")
    print("\n1. View account info")
    print("\n2. Transfer money to another wallet account")
    print("\n3. Deposit money")
    print("\n4. Withdraw money")
    print("\n5. View all transactions")
    print("\n6. exit")
    Choice = input("Enter an option:--> ")
    if Choice == '1':
        select_user_data(conn,username,password)
    elif Choice == '2':
        transfer_internal(conn,username,password)
    elif Choice == '3':
        Account_deposit(conn,username,password)
    elif Choice == '4':
        Account_withdrawal(conn,username,password)
    elif Choice == '5':
        view_log_user(conn,username,password)
    elif Choice == '6':
        exit()
    else:
        print("invalid input")
    userMenu(conn,username,password)

#HEADING
def logo():
    print("******************************************************************")
    print("| ____    .    _____          |\   /|  ~~~  |   | ____       |")
    print("| |      / \       /  \   /   | \ / | (   ) |\  | |    \   / |")
    print("| |__   /   \     /    \ /    |  .  | (   ) | \ | |__   \ /  |")
    print("| |    |_____|   /      |     |     | (   ) |  \| |      |   |")
    print("| |___ |     |  /____   |     |     |  ~~~  |   | |___   |   |")
    print("*****************************************************************\n")
#define basic info
database = "walletData.db"
conn = create_connection(database)

username = ""
password = ""

if __name__ == '__main__':
    main()