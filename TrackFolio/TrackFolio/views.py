from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
import bcrypt
from django.http import HttpResponse

def home(request):
    return render (request, 'home.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'error_display.html')

        # Encrypt password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = hashed_password.decode('utf-8')

        # Check if the username or email already exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", [username, email])
            user = cursor.fetchone()

            if user:
                messages.error(request, "Username or email already exists.")
                return render(request, 'error_display.html')

            # Insert new user into the database
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           [username, email, hashed_password])

        messages.success(request, "Account created successfully.")
        return redirect('login')

    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the user exists in the database
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", [username])
            user = cursor.fetchone()

            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                    request.session['user_id'] = user[0]
                    # messages.success(request, "Login successful.")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid username or password.")
            else:
                messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')




def dashboard(request):
    user_id = request.session.get('user_id')  # Assuming user ID is stored in session
    if not user_id:
        return redirect('login')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT portfolio_id, name
            FROM portfolio
            WHERE user_id = %s
        """, [user_id])
        portfolios = cursor.fetchall()  # Returns a list of tuples (portfolio_id, name)

    return render(request, 'dashboard.html', {'portfolios': portfolios})


def add_portfolio(request):
    user_id = request.session.get('user_id')  # Assuming user ID is stored in session
    if not user_id:
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        portfolio_type = request.POST.get('type')

        # Ensure both name and portfolio_type are provided
        if not name or not portfolio_type:
            return render(request, 'add_portfolio.html', {
                'error': 'Both name and type are required!'
            })


        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO portfolio (user_id, name, total_investment, current_value,
                                       sold_value, realised_gain, estimated_loss, today_gain_or_loss, type)
                VALUES (%s, %s, 0, 0, 0, 0, 0, 0, %s)
            """, [user_id, name, portfolio_type])

        return redirect('dashboard')  # Redirect to the dashboard after successful creation

    return render(request, 'add_portfolio.html')


def portfolio(request, portfolio_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT portfolio_id, name, type FROM portfolio WHERE portfolio_id = %s", [portfolio_id])
        portfolio = cursor.fetchone()  # Returns a single tuple (id, name, type) or None

    with connection.cursor() as cursor2:
        cursor2.execute("SELECT * FROM transaction WHERE portfolio_id = %s", [portfolio_id])
        transactions = cursor2.fetchall()  # Returns a list of tuples (id, name, type) or None

    if not portfolio:
        return redirect('home')  # Redirect if portfolio does not exist

    # Pass both 'portfolio' and 'transactions' inside a single dictionary
    context = {
        'portfolio': portfolio,
        'transactions': transactions
    }

    return render(request, 'portfolio.html', context)


def delete_portfolio(request, portfolio_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM portfolio WHERE portfolio_id = %s", [portfolio_id])

    return redirect('dashboard')  # Redirect to the list view



def add_transaction(request, portfolio_id):
    user_id = request.session.get('user_id')  # Assuming user ID is stored in session
    if not user_id:
        return redirect('login')
    print(f"request method is {request.method}")
    if request.method == "POST":
        transaction_type = request.POST.get('type')
        script = request.POST.get('stock')
        quantity = int(request.POST.get('quantity'))
        rate = float(request.POST.get('rate'))

        #calculation cost ammount
        ammount = quantity*rate

        #calculation of broker commision on the basis of price : b_commision = broker commision
        if ammount < 2500:
            b_commision = 10
        elif ammount > 2501 and ammount < 50000:
            b_commision = 0.0036*ammount
        elif ammount > 50001 and ammount < 500000:
            b_commision = 0.0033 * ammount
        elif ammount > 500001 and ammount < 2000001:
            b_commision = 0.0031 * ammount
        elif ammount > 2000001 and ammount < 10000000:
            b_commision = 0.0027*ammount
        else:
            b_commision = 0.0024 * ammount

        #calculation of sebon commision 0.15%
        s_commision = 0.00015 * ammount
        commision = b_commision + s_commision

        dp_charge = 25                  #dp charge = 25 (always)

        net_ammount = ammount + dp_charge + commision
        
        cps = net_ammount / quantity

        transaction_date = request.POST.get('transaction_date')

        with connection.cursor() as cursor:
            cursor.execute('''INSERT INTO transaction (portfolio_id, transaction_date, script, transaction_type, quantity, rate, comision, dp_charge, net_ammount, cps)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',[portfolio_id, transaction_date, script, transaction_type,quantity, rate, commision, dp_charge, net_ammount, cps])
        return redirect('portfolio',portfolio_id) 
        


    # views for rendering stock name from live data in template addtransaction.html

    from .livedata import fetch_live_stock_data  # Import the scraping function
    stocks = fetch_live_stock_data()  # Fetch the live stock data
    context = {'portfolio_id' : portfolio_id, 'stocks' : stocks}    #context part of render function cannot pass integer but only dictionary.

    return render(request, 'add_transaction.html', context=context)

   


def delete_transaction(request, portfolio_id, transaction_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM transaction WHERE portfolio_id = %s and transaction_id = %s", [portfolio_id, transaction_id])

    return redirect('portfolio', portfolio_id)  # Redirect to the list view

def view_transaction(request, portfolio_id, transaction_id):
    user_id = request.session.get('user_id')  # Assuming user ID is stored in session
    if not user_id:
        return redirect('login')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM transaction WHERE portfolio_id = %s and transaction_id = %s", [portfolio_id, transaction_id])
        transaction = cursor.fetchone()  # Returns a single tuple (id, name, type) or None
    context = {
        'portfolio_id': portfolio_id,
        'transaction': transaction
    }
    return render(request, 'view_transaction.html', context=context)   #passing transaction to view_transaction.html 

