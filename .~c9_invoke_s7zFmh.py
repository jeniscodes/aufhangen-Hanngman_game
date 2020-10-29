import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///words.db")




@app.route("/")
def index():
    """Show portfolio of stocks"""
    user=session['user_id']
    row= db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=session['user_id'])
    cash = row [0] ['cash']
    username= row [0] ['username']
    total= cash
    assets=[]
    asset=db.execute("SELECT * FROM asset WHERE username = :username",
                          username=username)

    if len(asset) > 0 :




        for row in asset:

            symbol=row['symbol']
            shares=row['share']
            stock=lookup(symbol)
            price=stock['price']
            name=stock['name']
            amount= shares * float(price)
            total+= amount
            assets.append({'symbol':symbol, 'shares':shares, 'price': usd(price), 'amount': usd(amount), 'name':name})





    return render_template ('index.html', assets = assets, cash = usd(cash), total = usd(total))




@app.route("/buy", methods=["GET", "POST"])
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("Valid symbol must be provided", 400)
        if not request.form.get("shares") or int(request.form.get("shares")) < 0:
            return apology("Valid share value must be provided", 400)

        try:
            stock=lookup(request.form.get("symbol"))
        except:
            return apology("Valid symbol must be provided", 400)

        name=stock['name']
        price=stock['price']
        symbol=stock['symbol']
        share=int(request.form.get("shares"))
        amount = price * share

        row= db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=session['user_id'])
        cash = row [0] ['cash']
        username= row [0] ['username']

        if cash < amount:
            return apology(" Your balance is not sufficient for this transaction", 400)

        db.execute("INSERT INTO 'transaction' ('username', 'name', 'symbol', 'log', 'share', 'amount') VALUES (:username, :name, :symbol, :log, :share, :amount)",
                      username=username , name=name, symbol = symbol, log = 'in', share = share, amount = amount)
        check=db.execute("SELECT * FROM asset WHERE username = :username AND symbol = :symbol",
                          username = username, symbol = symbol)
        if len(check) > 0:
            preshare = check [0] ['share']
            db.execute("UPDATE asset SET share= :postshare WHERE username = :username AND symbol = :symbol",
            postshare = share + preshare, username= username, symbol = symbol)
        else:
            db.execute("INSERT INTO 'asset' ('username', 'name', 'symbol', 'share') VALUES (:username, :name, :symbol, :share)",
            username=username , name=name, symbol = symbol, share = share)


        db.execute("UPDATE users SET cash= :cash WHERE username = :username", cash= cash-amount, username= username)

        flash(' Bought! ')
        return redirect("/")

    else:
        return render_template("buy.html")




@app.route("/history")
def history():
    """Show history of transactions"""
    user=session['user_id']
    row = db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=session['user_id'])
    username= row [0] ['username']
    print( username )
    rows = db.execute("SELECT * FROM 'transaction' WHERE username = :username",
                          username = username)
    history=[]
    for row in rows:

            symbol=row['symbol']
            shares=row['share']
            stock=lookup(symbol)
            price=stock['price']
            name=stock['name']
            transacted = row['createddate']
            history.append({'symbol':symbol, 'shares':shares, 'price': usd(price), 'transacted':transacted})


    return render_template("history.html", history = history)




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Valid symbol must be provided", 400)
        try:

            stock=lookup(request.form.get("symbol"))
            name=stock['name']
            price=stock['price']
            symbol=stock['symbol']
            return render_template("quoted.html", name=name, price=price, symbol=symbol)
        except:
            return apology("Valid symbol must be provided", 400)

    else:
        return render_template("quote.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation") or request.form.get("password")!=request.form.get("confirmation") :
            return apology("must provide password and conformation and they must match", 403)

        password = request.form.get("password")
        l, u, p, d = 0, 0, 0, 0
        print(password)

        if (len(password) < 8):
             return apology ("invalid password , must be 8 charatcers long with at least one lowercase, uppercase, number and symbol")

        else:

            for i in password:

                # counting lowercase alphabets
                if (i.islower()):
                    l+=1

                # counting uppercase alphabets
                if (i.isupper()):
                    u+=1

                # counting digits
                if (i.isdigit()):
                    d+=1

                # counting the mentioned special characters
                if(i=='@'or i=='$' or i=='_'):
                    p+=1

            print(p)

            if  (l<1 or u<1 or p<1 or d<1 or l+p+u+d != len(password)):
                return apology ("invalid password , must be 8 charatcers long with at least one lowercase, uppercase, number and symbol")


        # ensure no such username exist
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username doesnt exists
        if len(rows) == 1 :
            return apology("Username already exists", 403)

        # Query database for username
        user = db.execute("INSERT INTO users (username,hash) VALUES (:username,:hash)",
                          username=request.form.get("username"), hash= generate_password_hash(request.form.get("password")))



        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash(' Your account has been registered.')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("symbol must be provided", 400)
        row= db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=session['user_id'])
        cash = row [0] ['cash']
        username= row [0] ['username']
        row= db.execute("SELECT * FROM asset WHERE username = :username AND symbol= :symbol" ,
                          username = username, symbol = request.form.get("symbol") )
        shares_q= int(row [0] ['share'])
        if not request.form.get("shares") or int(request.form.get("shares")) > shares_q:
            return apology("Sorry, you dont have sufficient shares", 400)

        try:
            stock=lookup(request.form.get("symbol"))
        except:
            return apology("Valid symbol must be provided", 400)

        name=stock['name']
        price=stock['price']
        symbol=stock['symbol']
        share=shares_q-int(request.form.get("shares"))
        amount = price * int(request.form.get("shares"))
        sell_share=f'-{request.form.get("shares")}'

        db.execute("INSERT INTO 'transaction' ('username', 'name', 'symbol', 'log', 'share', 'amount') VALUES (:username, :name, :symbol, :log, :share, :amount)",
                      username=username , name=name, symbol = symbol, log = 'out', share = sell_share, amount = amount)


        db.execute("UPDATE  asset SET share= :share WHERE username = :username AND symbol = :symbol",
                      username=username , symbol = symbol, share = share)

        db.execute("UPDATE users SET cash= :cash WHERE username = :username", cash = cash + amount, username= username)
        db.execute("DELETE FROM asset WHERE share= :zero", zero = 0)
        flash(' Sold!')
        return redirect ("/")
    else:

        row= db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=session['user_id'])

        username= row [0] ['username']
        symbols= db.execute("SELECT symbol FROM asset WHERE username = :username",
                          username = username)

        symbolslist=[i['symbol'] for i in symbols]

        return render_template ("sell.html", symbols = symbolslist)









