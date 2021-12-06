import os
import requests
# import sqlite3
import json
from cs50 import SQL
from tempfile import mkdtemp
from datetime import datetime
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

# db = SQL("sqlite:////Users/Amulya Atluri/PycharmProjects/cs6360_my_db_proj/mysqlite_DB_COMMANDS.db")
db = SQL("sqlite:///mysqlite_DB_COMMANDS.db")


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

        y = db.execute("SELECT * from User")
        role = [w for w in y if w['USER_ID']==session['user_id']]
        print("role: ", role)
        # user = [z for z in x if z['CLIENT_ID'] == session['user_id']]
        
        print("\n role: ", role)
        g.role = role[0]['ROLE']
        g.user = role[0]['USERNAME']

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
        print("\n\n x1: ", x,"\n\n y1", y, "\n")

        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user_record = db.execute("SELECT HPWD, USER_ID from User where USERNAME = (?)", username)

        print("***** ", user_record, password)
        # user = [x for x in users if x.username == username][0]
        if user_record and user_record[0]['HPWD'] == password:

            user_id = user_record[0]['USER_ID']

            session['user_id'] = user_id

            role = db.execute("SELECT ROLE FROM User where USER_ID=(?)", user_id)[0]['ROLE']

            if role=='client':
                return redirect(url_for('profile'))
            else:
                return redirect(url_for('bitinfo'))

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
    bitcoin_value = round(float(requests.get('https://api.coindesk.com/v1/bpi/currentprice.json').json()["bpi"]["USD"]["rate"].replace(",", "")),2)

    total = 0.00
    counter = 0
    total_bitcoins = 0
    for i in previous_transactions:
        total_bitcoins = total_bitcoins + i["NUMBER_OF_BITCOINS"]
        total = total + round((float(i["NUMBER_OF_BITCOINS"]) * bitcoin_value),2)
        counter += 1
    # print("\n counter: ", counter)

    return render_template("profile.html", total_bitcoins=total_bitcoins, total=total, current_cash=current_cash)

############

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    exisiting_usernames = [x['USERNAME'] for x in db.execute("SELECT USERNAME FROM User")]
    print("exisiting_usernames: ", exisiting_usernames)
    error = None
    if request.method == 'POST':
        username = request.form['username']
        if username in exisiting_usernames:
            error = "Username is already taken, please use another username."
            return render_template('signup.html', error=error)
        else:
            fname = request.form['fname']
            lname = request.form['lname']
            password = request.form['password']
            street = request.form['street']
            city = request.form['city']
            zipcode = request.form['zip']
            state = request.form['state']
            email = request.form['email']
            phone = request.form['phone']
            cell = request.form['mobile']
            role = request.form.get("role")

            print("role: ", role)

            db.execute("INSERT INTO User(USERNAME, FNAME, LNAME, PHONE, CELL, EMAIL, ROLE, HPWD) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", username, fname, lname, phone, cell, email, role, password)
            rec = db.execute("SELECT USER_ID FROM User WHERE  USERNAME=(?)", username)
            print("!!! rec: ", rec)
            user_id = rec[0]['USER_ID']
            if role=='client':
                db.execute("INSERT INTO Client(CLIENT_ID) VALUES (?)", user_id)
                db.execute("INSERT INTO Address(CLIENT_ID, STREET, CITY, STATE, ZIP) VALUES(?, ?, ?, ?, ?)", user_id, street, city, state, zipcode )
            elif role=='trader':
                db.execute("INSERT INTO Trader(TRADER_ID) VALUES (?)", user_id)
            print("signup rec: ", rec)
            return render_template('login.html', msg="Account Created, You can Login now!")
    return render_template('signup.html', error=error)

############

@app.route("/")
def index():
    return render_template("index.html")

############

@app.route("/bitinfo")
@login_required
def bitinfo():
    # Get the fluctuating BitCoin value from API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://api.coindesk.com/v1/bpi/currentprice.json")
        data = response.json()
        bitvalue = round(float(data["bpi"]["USD"]["rate"].replace(",", "")),2)
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


@app.route('/trader_accept', methods=['POST', 'GET'])
@login_required
def trader_accept():
    user = session["user_id"]
    print(request.method)
    if(request.method == 'POST'):
        print('in posr')
        accept = request.form.get("accept/decline")
        print(accept)
        accept_json = json.loads(accept)
        print(accept_json)
        insert_query = "UPDATE MONEY_PAYMENT_TRANSACTIONS SET FINAL_STATUS = (?) WHERE CLIENT_ID = (?) AND TRADER_ID =(?) AND DATE_TIME = (?)"
        db.execute(insert_query,1 if accept_json["action"] == "accept" else 0,accept_json["client_id"],accept_json["trader_id"], accept_json["date_time"])
        
        if(accept_json["action"] == "accept"):
            q = db.execute("select net_amount from net_amount where  CLIENT_ID = (?) AND TRADER_ID =(?)",accept_json["client_id"],accept_json["trader_id"])
            db.execute("UPDATE CLIENT set LIQUID_CASH = LIQUID_CASH - (?) where client_id =(?)",accept_json["amount"],accept_json["client_id"])
            if(q):
                t = db.execute("UPDATE NET_AMOUNT SET NET_AMOUNT = NET_AMOUNT + (?) where CLIENT_ID = (?) AND TRADER_ID =(?)",accept_json["amount"],accept_json["client_id"],accept_json["trader_id"])
            else:
                t = db.execute("insert into net_amount (net_amount, client_id, trader_id) values (?,?,?)",accept_json["amount"],accept_json["client_id"],accept_json["trader_id"])
    t = db.execute("SELECT * from MONEY_PAYMENT_TRANSACTIONS WHERE TRADER_ID=(?) and FINAL_STATUS=0", user)
    print("\n\n ttt: ", t)
    return render_template("trader_accept.html",t=t)


# @app.route('/trader_btc_accept', methods=['POST', 'GET'])
# @login_required
# def trader_btc_accept():
#     user = session["user_id"]
#     t = db.execute("SELECT * from BITCOIN_TRANSACTIONS WHERE TRADER_ID=(?) AND FINAL_STATUS=0", user)
#     # print("\n\n edsaxfef: ", t)
#     print(request.method)
#     if(request.method == 'POST'):
#         print('in posr')
#         accept = request.form.get("accept/decline")
#         print(accept)
#         accept_json = json.loads(accept)
#         print(accept_json)
#         insert_query = "UPDATE BITCOIN_TRANSACTIONS SET FINAL_STATUS = (?) WHERE CLIENT_ID = (?) AND TRADER_ID =(?) AND DATE_TIME = (?)"
#         db.execute(insert_query,1 if accept_json["action"] == "accept" else 0,accept_json["client_id"],accept_json["trader_id"], accept_json["date_time"])
#         if(accept_json["action"] == "accept"):
#             t = db.execute("UPDATE NET_AMOUNT SET NET_AMOUNT = (NET_AMOUNT - (?) - (?)) where CLIENT_ID = (?) AND TRADER_ID =(?)",accept_json["AMOUNT"],accept_json["COMMISSION_AMOUNT"],accept_json["client_id"],accept_json["trader_id"])
#             t = db.execute("update client set no_of_bitcoins = no_of_bitcoins + (?) where client_id = (?)",accept_json['no_of_bitcoins'],accept_json['client_id'])
#         t = db.execute("SELECT * from BITCOIN_TRANSACTIONS WHERE TRADER_ID=(?) AND FINAL_STATUS=0", user)
#         print("\n\n ttt: ", t)
#     return render_template("trader_btc_accept.html",t=t)

##########
@app.route('/view_requests', methods=['POST', 'GET'])
@login_required
def view_requests():
    user = session["user_id"]
    t = db.execute("SELECT * from REQUESTS WHERE TRADER_ID=(?) and status = 0", user)
    print("\n\n ttt: ", t)
    if(request.method == 'POST'):
        response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
        
        if response.status_code == 500 or response.status_code == 404:
            flash("Something went wrong, Please try again.", "danger")
            return render_template("buy.html")
        data = round(float(response.json()["bpi"]["USD"]["rate"].replace(",", "")))

        accept = request.form.get("accept/decline")
        print(accept)
        accept_json = json.loads(accept)
        print(accept_json)
        commission_type = db.execute("select commision_type,NO_OF_BITCOINS from requests  WHERE CLIENT_ID = (?) AND TRADER_ID =(?) AND DATE_TIME = (?)",accept_json["client_id"],accept_json["trader_id"], accept_json["date_time"])
        insert_query = "UPDATE REQUESTS SET STATUS = (?) WHERE CLIENT_ID = (?) AND TRADER_ID =(?) AND DATE_TIME = (?)"
        
        print(commission_type)

        db.execute(insert_query,1 if accept_json["action"] == "accept" else -1,accept_json["client_id"],accept_json["trader_id"], accept_json["date_time"])
        client_data = db.execute("SELECT LIQUID_CASH, NO_OF_BITCOINS, MEMBERSHIP FROM Client WHERE CLIENT_ID = (?)", accept_json["client_id"])
        
        
        current_cash = client_data[0]['LIQUID_CASH']
        membership_type = client_data[0]['MEMBERSHIP']
        bitcoins_value = data * float(commission_type[0]['NO_OF_BITCOINS'])

        commission_amount = 0
        new_balance = current_cash
        if bitcoins_value > 0:
            if commission_type[0]['commision_type'] == 'crypto':
                if membership_type=='g':
                    bitcoins = (bitcoins_value*0.99)/float(data)
                else:
                    bitcoins = (bitcoins_value*0.98)/float(data)
            else:
                if membership_type=='g':
                    commission_amount = bitcoins_value*0.1
                    bitcoins = (bitcoins_value)/float(data)
                else:
                    commission_amount = bitcoins_value*0.2  
                    bitcoins = (bitcoins_value)/float(data)
            new_balance = current_cash - (bitcoins_value + commission_amount)
        else:
            bitcoins = ((bitcoins_value)/float(data))
        print(bitcoins)
        
        db.execute("insert into BITCOIN_TRANSACTIONS (NUMBER_OF_BITCOINS,PRICE,COMMISSION_TYPE,COMMISSION_AMOUNT,CLIENT_ID,TRADER_ID,FINAL_STATUS) values (?,?,?,?,?,?,?)",bitcoins,bitcoins_value,commission_type[0]['commision_type'],commission_amount,accept_json["client_id"],accept_json["trader_id"],1)
        db.execute("update client set liquid_cash = (?), no_of_bitcoins = no_of_bitcoins + (?) where client_id = (?)",new_balance,bitcoins,accept_json["client_id"])
        t = db.execute("SELECT * from REQUESTS WHERE TRADER_ID=(?) and status = 0", accept_json["trader_id"],)
        print("\n\n ttt: ", t)

    return render_template("view_requests.html",t=t)

@app.route('/client_info', methods=['POST', 'GET'])
@login_required
def client_info():
    user = session["user_id"]

    # t = db.execute("SELECT * from REQUESTS WHERE TRADER_ID=(?)", user)
    # print("\n\n ttt: ", t)
    cn = cc = cs = cz =cst =None
    if(request.method == 'POST'):
        cn = request.form.get("Client_Name") +'%'
        print(cn)
        cst = request.form.get("Client_Street") +'%'
        print(cst)
        cc = request.form.get("Client_City") +'%'
        print(cc)
        cs = request.form.get("Client_State") +'%'
        print(cs)
        cz = request.form.get("Client_Zip") +'%'
        print(cz)

    query = "SELECT u.username,A.STREET ,A.CITY , A.STATE ,A.ZIP ,bt.NUMBER_OF_BITCOINS,bt.price,bt.DATE_TIME\
    ,bt.COMMISSION_TYPE,bt.COMMISSION_AMOUNT,bt.FINAL_STATUS FROM Client c , User U, Address A, BITCOIN_TRANSACTIONS bt\
     where c.CLIENT_ID = U.USER_ID and c.CLIENT_ID =A.CLIENT_ID and bt.CLIENT_ID = c.CLIENT_ID and u.username LIKE '{}' \
     and bt.TRADER_ID ='{}' and A.STREET LIKE '{}' and A.city LIKE '{}' and A.STATE LIKE '{}' and ZIP LIKE '{}'".format(cn, user,cst,cc,cs,cz)
    print(query)
    t = db.execute(query)
    # t = db.execute("SELECT u.username,A.STREET ,A.CITY , A.STATE ,A.ZIP ,bt.NUMBER_OF_BITCOINS,bt.price,bt.DATE_TIME\
    # ,bt.COMMISSION_TYPE,bt.COMMISSION_AMOUNT,bt.FINAL_STATUS FROM Client c , User U, Address A, BITCOIN_TRANSACTIONS bt\
    #  where c.CLIENT_ID = U.USER_ID and c.CLIENT_ID =A.CLIENT_ID and bt.CLIENT_ID = c.CLIENT_ID and u.username=(?) \
    #  and bt.TRADER_ID =(?) and A.STREET LIKE (?) and A.city LIKE (?) and A.STATE LIKE (?) and ZIP LIKE (?)",cn, user,cst,cc,cs,cz)
        # t = db.execute("SELECT * from REQUESTS WHERE TRADER_ID=(?)", user)
    print("\n\n asdddsdfdfsdfsfsdfd: ", t)

    return render_template("client_info.html",t=t)

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
        data = round(float(response.json()["bpi"]["USD"]["rate"].replace(",", "")))
        user = session["user_id"]
        print("\n uuu: userid:", user, " bitcoins: ", bitcoins, " commission_type: ", commission_type, " bitvalue: ", data)

        # current_cash = sqlite3.execute("SELECT LIQUID_CASH, NO_OF_BITCOINS FROM Client WHERE id = (?)", user)

        client_data = db.execute("SELECT LIQUID_CASH, NO_OF_BITCOINS, MEMBERSHIP FROM Client WHERE CLIENT_ID = (?)", user)
        print("\n @@@ client_data:", client_data, "\n")

        print()

        # if user in Client Table
        no_of_bitcoins = 0
        bitcoins_value = 0
        new_balance = 0
        if client_data:
            print("\n\n ### Entered : if client_data")
            no_of_bitcoins = client_data[0]['NO_OF_BITCOINS']
            current_cash = client_data[0]['LIQUID_CASH']
            membership_type = client_data[0]['MEMBERSHIP']
            bitcoins_value = data * float(bitcoins)

            # curr_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            curr_datetime = datetime.now()
            curr_month = curr_datetime.date().month
            # curr_month = 1
            curr_year = curr_datetime.date().year
            # curr_year = 2022
            desired_month = curr_month-1
            desired_year = curr_year
            if curr_month==1:
                desired_month = 12
                desired_year = curr_year-1

            print("Current month is: ", curr_month)
            print("Desired month is: ", desired_month, " Desired year is: ", desired_year)

            txn_data = db.execute("SELECT DATE_TIME, strftime('%Y', DATE_TIME), strftime('%m', DATE_TIME), NUMBER_OF_BITCOINS, PRICE FROM BITCOIN_TRANSACTIONS WHERE CLIENT_ID = (?) AND FINAL_STATUS=1", user)
            print("txn_data: ", txn_data)

            client_prev_txn_data = db.execute("SELECT DATE_TIME, NUMBER_OF_BITCOINS, PRICE FROM BITCOIN_TRANSACTIONS WHERE CLIENT_ID = (?) AND strftime('%Y', DATE_TIME)=(?) AND strftime('%m', DATE_TIME)=(?) AND FINAL_STATUS=1", user, str(desired_year), str(desired_month))
            print("client_prev_txn_data: ", client_prev_txn_data)

            prev_txn_value = 0
            if client_prev_txn_data:
                
                for d in client_prev_txn_data:
                    prev_txn_value = prev_txn_value + abs(d['NUMBER_OF_BITCOINS'])*d['PRICE']

            print("prev_txn_value: ", prev_txn_value)

            if prev_txn_value>100000:
                membership_type='g'
                print("goldddddddd")
                db.execute("UPDATE Client SET MEMBERSHIP = (?)  WHERE CLIENT_ID = (?)", 'g', user)

            else:
                membership_type='s'
                db.execute("UPDATE Client SET MEMBERSHIP = (?)  WHERE CLIENT_ID = (?)", 's', user)

            commission_amount = 0

            if commission_type == 'crypto':
                if membership_type=='g':
                    bitcoins = (bitcoins_value*0.99)/float(data)
                else:
                    bitcoins = (bitcoins_value*0.98)/float(data)
            else:
                if membership_type=='g':
                    commission_amount = bitcoins_value*0.1
                else:
                    commission_amount = bitcoins_value*0.2  
           
            new_balance = current_cash - (bitcoins_value + commission_amount)
            
            # new_balance = current_cash - bitcoins_value

        #if valid stock and user has enough funds
        if new_balance >= 0:
            print("\n\n !!! new_balance: ", new_balance)
            #  ##################################### to add fields for the COMMISSION_TYPE, COMMISSION_AMOUNT in the form, and plug those values below ############
            #  ##################################### add the membership upgradation and consideration code #######
            db.execute("INSERT INTO BITCOIN_TRANSACTIONS (CLIENT_ID, NUMBER_OF_BITCOINS, PRICE, COMMISSION_TYPE, COMMISSION_AMOUNT, FINAL_STATUS) VALUES (?, ?, ?, ?, ?, ?)", user, bitcoins, data, commission_type, commission_amount, 1)
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

# ####################################################################################

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        return render_template("sell.html")
    else:
        bitcoins = float(request.form.get("bitcoins"))
        user = session["user_id"]
        current_bitcoins = float(db.execute("SELECT NO_OF_BITCOINS FROM Client WHERE CLIENT_ID = (?)", user)[0]["NO_OF_BITCOINS"])

        # user does not own stock
        if current_bitcoins==0:
            error = "You do not own any bitcoins to sell."
            return render_template("sell.html", error=error)

        # user tried to sell more shares than they own
        elif current_bitcoins < bitcoins:
            error = "You are trying to sell more number of bitcoins than you own. Please select smaller number."
            return render_template("sell.html", error=error)

        # else
        else:
            response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
            current_cash = db.execute("SELECT LIQUID_CASH FROM Client WHERE CLIENT_ID = (?)", user)
            current_cash = current_cash[0]['LIQUID_CASH']
            bitvalue = float(response.json()["bpi"]["USD"]["rate"].replace(",", ""))
            new_balance = current_cash + ( bitvalue * float(bitcoins))
            bitcoins_left = current_bitcoins-bitcoins

            # update cash balance and number of bitcoins left
            db.execute("UPDATE Client SET LIQUID_CASH = (?), NO_OF_BITCOINS = (?) WHERE CLIENT_ID = (?)", new_balance, bitcoins_left, user)
            
            # if current_bitcoins == bitcoins:
            #     # update portfolio
            #     db.execute("DELETE FROM BITCOIN_TRANSACTIONS WHERE CLIENT_ID = (?)", user)
            # elif current_bitcoins > bitcoins:
            #     db.execute("UPDATE Client SET LIQUID_CASH = (?) WHERE CLIENT_ID = (?)", new_balance, user)

            # update history
            db.execute("INSERT INTO BITCOIN_TRANSACTIONS(CLIENT_ID, NUMBER_OF_BITCOINS, PRICE, COMMISSION_TYPE, COMMISSION_AMOUNT, FINAL_STATUS) VALUES (?, ?, ?, ?, ?, ?)", user, "-"+str(bitcoins), bitvalue, "-", "12", 1)

            # db.execute("INSERT INTO BITCOIN_TRANSACTIONS(user_id, stock, shares, price) VALUES (?, ?, ?, ?)", user, symbol, "-" + shares, price.json()["latestPrice"])
            flash("Sold!", "primary")
            return redirect("/history")
        return "error 500"

# ####################################################################################

@app.route('/history')
@login_required
def history():

    user = session["user_id"]

    previous_bitcoin_transactions = db.execute("SELECT * FROM BITCOIN_TRANSACTIONS WHERE CLIENT_ID = (?)", user)
    previous_moneyPayment_transactions = db.execute("SELECT * FROM MONEY_PAYMENT_TRANSACTIONS WHERE CLIENT_ID = (?)", user)
    print("history: previous_bitcoin_transactions:", previous_bitcoin_transactions, " previous_moneyPayment_transactions: ",previous_moneyPayment_transactions)
    return render_template("history.html", previous_bitcoin_transactions=previous_bitcoin_transactions, previous_moneyPayment_transactions=previous_moneyPayment_transactions)



@app.route('/requestTrader',methods=["GET", "POST"])
@login_required
def request_a_trader():
    if request.method=="GET":
        return render_template("requestTrader.html")
    else:
        client_id = session["user_id"]
        trader_username = request.form.get("trader_username")
        print(type(trader_username))
        print(trader_username)
        action = request.form.get("trader_action")
        bitcoins = float(request.form.get("bitcoins"))
        trader_id = db.execute("SELECT USER_ID from User where USERNAME = (?)", trader_username)
        print("---------------------------------------------")
        print(trader_id)
        trader = db.execute("SELECT TRADER_ID from Trader where TRADER_ID = (?)", trader_id[0]["USER_ID"])
        print("Traders fectched: ",trader)
        print("TTTTTT")
        if trader:
            if action=='sell':
                client_current_bitcoins = db.execute("SELECT NO_OF_BITCOINS FROM Client WHERE CLIENT_ID = (?)", client_id)[0]["NO_OF_BITCOINS"]
                print("client_current_bitcoins: ", client_current_bitcoins, "bitcoins: ", bitcoins, "client_current_bitcoins>=bitcoins: ",client_current_bitcoins<=bitcoins)
                if client_current_bitcoins>=bitcoins:
                    # final status = -1 means declined by trader, 0: pending, 1: accepted by the trader
                    db.execute("INSERT INTO REQUESTS (CLIENT_ID, TRADER_ID, NO_OF_BITCOINS, STATUS, COMMISION_TYPE) VALUES (?, ?, ?, ?)", client_id, trader_id[0]["USER_ID"], -1*bitcoins, 0, request.form.get("commision_type"))
                    success_msg = "Request Sent the Trader, Let's wait for the approval!"
                    return render_template("requestTrader.html", success_msg=success_msg)
                else:
                    error = "You don’t have sufficient bitcoins to sell!"
                    return render_template("requestTrader.html", error=error)
            else:
                print("Entered Buy")
                db.execute("INSERT INTO REQUESTS (CLIENT_ID, TRADER_ID, NO_OF_BITCOINS, STATUS, COMMISION_TYPE) VALUES (?, ?, ?, ?, ?)", client_id, trader_id[0]["USER_ID"], bitcoins, 0, request.form.get("commision_type"))
                success_msg = "Request Sent the Trader, Let's wait for the approval!"
                return render_template("requestTrader.html", success_msg=success_msg)
        return render_template("requestTrader.html", error="Trader not found.")




@app.route('/payTrader', methods=["GET", "POST"])
@login_required
def pay_to_trader():
    if request.method == "GET":
        return render_template("payTrader.html")
    else:
        client_id = session["user_id"]
        trader_username = request.form.get("trader_username")
        amount = float(request.form.get("amount"))
        trader = db.execute("SELECT USER_ID from User where USERNAME = (?)", trader_username)
        if trader:
            trader_id = trader[0]['USER_ID']
        else:
            error = "No such trader exists!"
            return render_template("payTrader.html", error=error)
        client_current_cash = float(db.execute("SELECT LIQUID_CASH FROM Client WHERE CLIENT_ID = (?)", client_id)[0]['LIQUID_CASH'])
        a = db.execute("SELECT TRADER_ID from Trader where TRADER_ID = (?)", trader_id)
        print(a)
        if a:
            if amount<=client_current_cash:
                # net_amount = db.execute("SELECT NET_AMOUNT from NET_AMOUNT where TRADER_ID = (?) AND CLIENT_ID = (?)", trader_id, client_id)
                # net_amount = net_amount + amount
                # diff = client_current_cash - amount
                # db.execute("UPDATE Client SET LIQUID_CASH = (?) WHERE CLIENT_ID = (?)", diff, client_id)
                db.execute("INSERT INTO MONEY_PAYMENT_TRANSACTIONS (CLIENT_ID, TRADER_ID, AMOUNT, FINAL_STATUS) VALUES (?, ?, ?, ?)", client_id, trader_id, amount, 0)
                # db.execute("INSERT INTO NET_AMOUNT (CLIENT_ID, TRADER_ID, NET_AMOUNT) VALUES (?, ?, ?)", client_id, trader_id, amount)

                success_msg = "Money Sent to the Trader, Let's wait for the approval!"
                return render_template("payTrader.html", success_msg=success_msg)
            else:
                error = "You don’t have sufficient funds, Please add some to your wallet and then request a trader."
                return render_template("payTrader.html", error=error)
        else:
            error = "There exists no trader with the given username."
            return render_template("payTrader.html", error=error)


if __name__ == "__main__":
    app.run(debug=True, port="4114")