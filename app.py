import os
import requests
# import sqlite3
from cs50 import SQL
from tempfile import mkdtemp
from flask_session import Session
from functools import wraps
from flask import flash
from flask import g, redirect, url_for, session
from flask import Flask, request, render_template

# Define a flask app
app = Flask(__name__)
app.secret_key = 'super secret key'

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///mysqlite_DB_COMMANDS.db")

db = SQL("sqlite:////Users/vag/Documents/dbproj/mysqlite_DB_COMMANDS.db")
# db = sqlite3.connect("sqlite:///mysqlite_DB_COMMANDS.db")

######## dummy class to test role-based access ######### 
class User:
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

    def __repr__(self):
        return f'<User: {self.username}>'

users = []

users.append(User(id=1, username='Anthony', password='password', role='c'))
users.append(User(id=2, username='Becca', password='secret', role='a'))
users.append(User(id=3, username='Carlos', password='somethingsimple', role='t'))

######## dummy #########


############## change this to triggers ###########
db.execute("DELETE FROM User")
db.execute("INSERT INTO User(USERNAME, FNAME, LNAME, PHONE, CELL, EMAIL, ROLE, HPWD) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 'Anthony', 'Anthony', 'Temoc','1212121212','1111111111','anthony@gmail.com','c','password')
userid = db.execute("SELECT USER_ID from User where USERNAME=(?)","Anthony")[0]['USER_ID']
db.execute("INSERT INTO Client(CLIENT_ID) VALUES (?)", userid)
x = db.execute("SELECT * from Client")
y = db.execute("SELECT * from User")
# print("\n\n x0: ", x,"\n\n y0", y, "\n")

db.execute("INSERT INTO User(USERNAME, FNAME, LNAME, PHONE, CELL, EMAIL, ROLE, HPWD) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 'Bill', 'Bill', 'Temoc','1212121333','1111111333','bill@gmail.com','c','password')
userid = db.execute("SELECT USER_ID from User where USERNAME=(?)","Bill")[0]['USER_ID']
db.execute("INSERT INTO Client(CLIENT_ID) VALUES (?)", userid)
x = db.execute("SELECT * from Client")
y = db.execute("SELECT * from User")
# print("\n\n x0: ", x,"\n\n y0", y, "\n")

# d.execute("CREATE TRIGGER add_to_client_table AFTER INSERT ON User BEGIN INSERT INTO Client SELECT CASE WHEN NEW.email NOT LIKE '%_@__%.__%' THEN END")


db.execute("INSERT INTO User(USERNAME, FNAME, LNAME, PHONE, CELL, EMAIL, ROLE, HPWD) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 'Becca', 'Becca', 'Temoc','1212121222','1111111122','becca@gmail.com','a','password')
userid = db.execute("SELECT USER_ID from User where USERNAME=(?)","Becca")[0]['USER_ID']
db.execute("INSERT INTO Client(CLIENT_ID) VALUES (?)", userid)
x = db.execute("SELECT * from Client")
y = db.execute("SELECT * from User")
# print("\n\n x0: ", x,"\n\n y0", y, "\n")

db.execute("INSERT INTO User(USERNAME, FNAME, LNAME, PHONE, CELL, EMAIL, ROLE, HPWD) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 'Carlos', 'Carlos', 'Temoc','1212121233','1111111133','carlos@gmail.com','t','password')
userid = db.execute("SELECT USER_ID from User where USERNAME=(?)","Carlos")[0]['USER_ID']
db.execute("INSERT INTO Client(CLIENT_ID) VALUES (?)", userid)
x = db.execute("SELECT * from Client")
y = db.execute("SELECT * from User")
# print("\n\n x0: ", x,"\n\n y0", y, "\n")
##############

# x = db.execute("SELECT * from Client")
# print("\n\n xxx: ", x)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        print("\n session['user_id]:", session['user_id'])
    #     for z in x:
            # print("\n zz:",z)
        user = [z for z in x if z['CLIENT_ID'] == session['user_id']]
        role = [w for w in y if w['USER_ID']==session['user_id']]
        print("\n user: ", user, " role: ", role)
        g.role = role[0]['ROLE']
        g.username = role[0]['USERNAME']
        g.user = user
        print("\n g:", g.user)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':

        x = db.execute("SELECT * from Client")
        y = db.execute("SELECT * from User")
        print("\n\n x1: ", len(x),"\n\n y1", len(y), "\n")
        # print("\n\n x1: ", x,"\n\n y1", y, "\n")

        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user_record = db.execute("SELECT HPWD, USER_ID from User where USERNAME = (?)", username)

        print("***** ", user_record, password)
        # user = [x for x in users if x.username == username][0]
        if user_record and user_record[0]['HPWD'] == password:

            session['user_id'] = user_record[0]['USER_ID']
            return redirect(url_for('profile'))

        error = "Invalid credentials"

        return render_template('login.html', error=error)

    return render_template('login.html')

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route('/profile')
@login_required
def profile():

    user = session["user_id"]

    previous_transactions = db.execute("SELECT NUMBER_OF_BITCOINS, DATE_TIME FROM BITCOIN_TRANSACTIONS WHERE CLIENT_ID = (?)", user)
    current_cash = db.execute("SELECT LIQUID_CASH FROM Client WHERE CLIENT_ID = (?)", user)

    print("\n\n$$$", len(previous_transactions), len(current_cash), "****\n\n")
    current_cash = current_cash[0]['LIQUID_CASH']
    bitcoin_value = float(requests.get('https://api.coindesk.com/v1/bpi/currentprice.json').json()["bpi"]["USD"]["rate"].replace(",", ""))

    total = 0.00
    counter = 0
    for i in previous_transactions:
        total = total + (int(i["NUMBER_OF_BITCOINS"]) * bitcoin_value)
        counter += 1
    # print("\n counter: ", counter)

    return render_template("profile.html", previous_transactions=previous_transactions, bitcoin_value=bitcoin_value, current_cash=current_cash, total=total)

############

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

############

@app.route("/")
def index():
    return render_template("index.html")

############

@app.route("/bitinfo")
def bitinfo():
    # Get the fluctuating BitCoin value from API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://api.coindesk.com/v1/bpi/currentprice.json")
        data = response.json()
        bitvalue = float(data["bpi"]["USD"]["rate"].replace(",", ""))
        print("y3", bitvalue) 
        print("Y1")
        response.raise_for_status()
        print("y2")
        return render_template("bitinfo.html", price=bitvalue)
    except requests.RequestException:
        print("n1")
        return None

############

@app.route('/addToWallet', methods=['POST', 'GET'])
@login_required
def add_to_wallet():
    """Buy BitCoins"""

    if request.method == "GET":
        return render_template("addmoney.html")

    else:
        amount = request.form.get("amount")

        print("\n AA: amount:", amount)
        user = session["user_id"]

        a = db.execute("SELECT LIQUID_CASH FROM Client WHERE CLIENT_ID = (?)", user)
        print("\n a: ", a)
        if a:
            total = float(amount) + float(a[0]['LIQUID_CASH'])
            db.execute("UPDATE Client SET LIQUID_CASH = (?) WHERE CLIENT_ID = (?)", total, user)
            b = db.execute("SELECT LIQUID_CASH FROM Client WHERE CLIENT_ID = (?)", user)[0]['LIQUID_CASH']
            print(b)
            print('b-a:', b-float(a[0]['LIQUID_CASH']), ' amount:', amount)
            if b-float(a[0]['LIQUID_CASH'])==amount:
                print("\n Yes!!")
                flash("Something went wrong, Please try again.", "danger")
            return redirect(url_for('profile'))
        return "Something Unexpected!"

##########

@app.route('/buy', methods=['POST', 'GET'])
@login_required
def buy():
    """Buy BitCoins"""

    if request.method == "GET":
        return render_template("buy.html")

    else:
        bitcoins = request.form.get("bitcoins")
        commission = request.form.get("commission")
        commission_type = "fiat"
        if commission=="crypto":
            commission_type = "crypto"
        response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
        # if invalid ticker
        if response.status_code == 500 or response.status_code == 404:
            flash("Something went wrong, Please try again.", "danger")
            return render_template("buy.html")
        data = float(response.json()["bpi"]["USD"]["rate"].replace(",", ""))
        user = session["user_id"]
        print("\n uuu: userid:", user, " bitcoins: ", bitcoins, " commission_type: ", commission_type, " bitvalue: ", data)

        # current_cash = sqlite3.execute("SELECT LIQUID_CASH, NO_OF_BITCOINS FROM Client WHERE id = (?)", user)

        current_cash = db.execute("SELECT LIQUID_CASH, NO_OF_BITCOINS FROM Client WHERE CLIENT_ID = (?)", user)
        print("\n @@@ current_cash:", current_cash, "\n")

        print()

        # if user in Client Table
        no_of_bitcoins = 0
        bitcoins_value = 0
        new_balance = 0
        if current_cash:
            print("\n\n ### current_cash: ", current_cash)
            no_of_bitcoins = current_cash[0]['NO_OF_BITCOINS']
            current_cash = current_cash[0]['LIQUID_CASH']
            bitcoins_value = data * float(bitcoins)
            new_balance = current_cash - bitcoins_value

        #if valid stock and user has enough funds
        if new_balance >= 0:
            print("\n\n !!! new_balance: ", new_balance)
            #  ##################################### to add fields for the COMMISSION_TYPE, COMMISSION_AMOUNT in the form, and plug those values below ############
            #  ##################################### add the membership upgradation and consideration code #######
            db.execute("INSERT INTO BITCOIN_TRANSACTIONS (CLIENT_ID, NUMBER_OF_BITCOINS, PRICE, COMMISSION_TYPE, COMMISSION_AMOUNT, FINAL_STATUS) VALUES (?, ?, ?, ?, ?, ?)", user, bitcoins, bitcoins_value, commission_type, 12, 1)
            #  #####################################

            db.execute("UPDATE Client SET LIQUID_CASH = (?), NO_OF_BITCOINS = (?)  WHERE CLIENT_ID = (?)", new_balance, float(bitcoins)+float(no_of_bitcoins), user)
            print("\n\n KK:",user)
            x = db.execute("SELECT * from Client")
            print("\n\n xxx: ", x)
            t = db.execute("SELECT * from BITCOIN_TRANSACTIONS WHERE CLIENT_ID=(?)", user)
            print("\n\n ttt: ", t)
            flash("Bought!", "primary")
            return redirect("/profile")

        # if not enough funds in account
        elif new_balance < 0:
            print("\n\n @@@ Entered else in Buy!!!\n\n")
            error = "You do not have enough funds in account."
            return render_template("buy.html", error=error)

@app.route('/history')
@login_required
def history():

    user = session["user_id"]

    previous_transactions = db.execute("SELECT NUMBER_OF_BITCOINS, DATE_TIME FROM BITCOIN_TRANSACTIONS WHERE CLIENT_ID = (?)", user)
    current_cash = db.execute("SELECT LIQUID_CASH FROM Client WHERE CLIENT_ID = (?)", user)

    print("\n\n$$$", len(previous_transactions), len(current_cash), "****\n\n")
    current_cash = current_cash[0]['LIQUID_CASH']
    bitcoin_value = float(requests.get('https://api.coindesk.com/v1/bpi/currentprice.json').json()["bpi"]["USD"]["rate"].replace(",", ""))

    total = 0.00
    counter = 0
    for i in previous_transactions:
        total = total + (int(i["NUMBER_OF_BITCOINS"]) * bitcoin_value)
        counter += 1
    # print("\n counter: ", counter)

    return render_template("history.html", previous_transactions=previous_transactions, bitcoin_value=bitcoin_value, current_cash=current_cash, total=total)
    


if __name__ == "__main__":
    app.run(debug=True, port="4114")