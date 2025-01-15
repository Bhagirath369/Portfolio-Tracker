# # from django.shortcuts import render


# # def home(request):
# #     return render(request, "signup.html")

# # def login(request):
# #     return render(request, "login.html")

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
import bcrypt

# def home(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         confirm_password = request.POST['confirm_password']

#         if password != confirm_password:
#             messages.error(request, "Passwords do not match.")
#             return redirect('signup')

#         # Encrypt password using bcrypt
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

#         # Check if the username or email already exists
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", [username, email])
#             user = cursor.fetchone()

#             if user:
#                 messages.error(request, "Username or email already exists.")
#                 return redirect('signup')

#             # Insert new user into the database
#             cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
#                            [username, email, hashed_password])

#         messages.success(request, "Account created successfully.")
#         return redirect('login')

#     return render(request, 'signup.html')



# def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']

#         # Check if the user exists in the database
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM users WHERE username=%s", [username])
#             user = cursor.fetchone()

#             if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
#                 # Password matches, set session data
#                 request.session['user_id'] = user[0]
#                 messages.success(request, "Login successful.")
#                 return redirect('dashboard')
#             else:
#                 messages.error(request, "Invalid username or password.")
#                 return redirect('login')

#     return render(request, 'login.html')

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
import bcrypt

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
                    return redirect('home')
                else:
                    messages.error(request, "Invalid username or password.")
            else:
                messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')




def home(request):
    # if 'user_id' not in request.session:
    #      # If the user is not logged in, redirect to login page
    #      return redirect('login')

    # Otherwise, render the home page
    #return render(request, 'home.html')

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

    return render(request, 'home.html', {'portfolios': portfolios})


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

        return redirect('home')  # Redirect to the dashboard after successful creation

    return render(request, 'add_portfolio.html')


def portfolio(request, portfolio_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT portfolio_id, name, type FROM portfolio WHERE portfolio_id = %s", [portfolio_id])
        portfolio = cursor.fetchone()  # Returns a single tuple (id, name, type) or None

    if not portfolio:
        return redirect('home')  # Redirect if portfolio does not exist

    return render(request, 'portfolio.html', {'portfolio': portfolio})
    

def delete_portfolio(request, portfolio_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM portfolio WHERE portfolio_id = %s", [portfolio_id])

    return redirect('home')  # Redirect to the list view







