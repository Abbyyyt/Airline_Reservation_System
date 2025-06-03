from flask import Flask, render_template, request, url_for, redirect, session,flash
import mysql.connector
import random
from datetime import datetime, timedelta
from mysql.connector.cursor import MySQLCursorDict
import json
from decimal import Decimal
import re
#Initialize the app from Flask
app = Flask(__name__)
from datetime import datetime

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%b %Y'):
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return value  # Return original if format doesn't match
    return value.strftime(format)

# Configure MySQL
# conn = mysql.connector.connect(host='localhost',
#                                user='root',
#                                password='',
#                                database='blog')

conn2 = mysql.connector.connect(host='localhost',
                               user='root',
                               password='',
                               database='air_ticket_reservation_system')
                            

#Define a route to hello function
@app.route('/')
def hello():
    # if 'username' in session:
    #     return redirect(url_for('home'))
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

#Define route for register Customer
@app.route('/registerforCustomer')
def registerforCustomer():
	return render_template('registerforCustomer.html')

#Define route for register Bookingagent
@app.route('/registerforBookingagent')
def registerforBookingagent():
    return render_template('registerforBookingagentsecond.html')



#Define route for register staff
@app.route('/registerforStaff')
def registerforStaff():
	return render_template('registerforStaff.html')

#Define route for view public info
@app.route('/public', methods=['GET', 'POST'])
def public():
    try:
        cursor = conn2.cursor(dictionary=True)
        
        coming_flights = []
        error = None
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'search_flights':
                source = request.form.get('source', '').strip()
                destination = request.form.get('destination', '').strip()
                departure_date = request.form.get('departure_date', '').strip()
                flight_num = request.form.get('flight_num', '').strip()
                
                query = """
                    SELECT f.airline_name, f.flight_num, f.departure_airport, f.departure_time, 
                        f.arrival_airport, f.arrival_time, f.price, f.status
                    FROM flight f
                    JOIN airport a1 ON f.departure_airport = a1.airport_name
                    JOIN airport a2 ON f.arrival_airport = a2.airport_name
                    WHERE f.departure_time > NOW()
                """
                params = []
                
                if source:
                    query += " AND (a1.airport_city = %s OR a1.airport_name = %s)"
                    params.extend([source, source])
                if destination:
                    query += " AND (a2.airport_city = %s OR a2.airport_name = %s)"
                    params.extend([destination, destination])
                if departure_date:
                    query += " AND DATE(f.departure_time) = %s"
                    params.append(departure_date)
                if flight_num:
                    query += " AND f.flight_num = %s"
                    params.append(flight_num)
                
                query += " ORDER BY f.departure_time"
                cursor.execute(query, params)
                coming_flights = cursor.fetchall()
                
                if not coming_flights and (source or destination or departure_date or flight_num):
                    error = "No flights found matching your criteria."
        
        if not coming_flights and request.method == 'GET':
            query = """
                SELECT airline_name, flight_num, departure_airport, departure_time, 
                    arrival_airport, arrival_time, price, status
                FROM flight
                WHERE departure_time > NOW()
                ORDER BY departure_time
            """
            cursor.execute(query)
            coming_flights = cursor.fetchall()
        
        # cursor.close()
        return render_template('public.html', coming_flights=coming_flights, error=error)
    
    except mysql.connector.errors.OperationalError as e:
        # Catch the OperationalError and redirect to the error page
        print(f"Database error: {e}")
        return redirect(url_for('error'))

@app.route('/error')
def error():
    # Render the error page with a user-friendly message
    return render_template('error.html')

#Authenticates the login
@app.route('/loginAuth', methods=['POST'])
def loginAuth():
    try:
        # Grabs info from form
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        cursor = conn2.cursor()
        error = None
        data = None

        # Build query based on user type
        if user_type == "customer":
            query = "SELECT * FROM customer WHERE email = %s AND password = %s"
            cursor.execute(query, (username, password))
            data = cursor.fetchone()
        elif user_type == "booking_agent":
            query = "SELECT * FROM booking_agent WHERE email = %s AND password = %s"
            cursor.execute(query, (username, password))
            data = cursor.fetchone()
        elif user_type == "airline_staff":
            query = "SELECT * FROM airline_staff WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            data = cursor.fetchone()
        # cursor.close()

        if data:
            session['username'] = username
            session['user_type'] = user_type

            if user_type == "customer":
                return redirect(url_for('home_Customer'))
            elif user_type == "booking_agent":
                #session['agent_id'] = data['booking_agent_id']  # store agent ID for later queries
                return redirect(url_for('home_BookingAgent'))
            elif user_type == "airline_staff":
                query2 = "SELECT permission_type FROM permission WHERE username = '{}'".format(username)
                query3 = "SELECT airline_name FROM airline_staff WHERE username = '{}'".format(username)
                cursor2 = conn2.cursor(buffered=True)
                cursor2.execute(query2)
                data2 = cursor2.fetchone()
                cursor3 = conn2.cursor(buffered=True)
                cursor3.execute(query3)
                data3 = cursor3.fetchone()
                # cursor2.close()
                # cursor3.close()
                session['permission'] = data2[0] if data2 else None    ###改了###
                session['airline_name'] = data3[0]
                return redirect(url_for('home_AirlineStaff'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    
    except mysql.connector.errors.OperationalError as e:
        # Catch the OperationalError and redirect to the error page
        print(f"Database error: {e}")
        return redirect(url_for('error'))


#Authenticates the register for Customer
@app.route('/registerAuthCustomer', methods=['GET', 'POST'])
def registerAuthCustomer():
    try:
        password = request.form.get('password')
        email = request.form.get('email')
        name = request.form.get('name')
        building_number = request.form.get('building_number')
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        phone_number = request.form.get('phone_number')
        passport_number = request.form.get('passport_number')
        passport_expiration = request.form.get('passport_expiration')
        passport_country = request.form.get('passport_country')
        date_of_birth = request.form.get('date_of_birth')

        cursor = conn2.cursor()

        # Check if user already exists
        query = "SELECT * FROM customer WHERE email = %s"
        cursor.execute(query, (email,))
        data = cursor.fetchone()
        error = None

        if data:
            error = "This user already exists"
            return render_template('registerforCustomer.html', error=error)
        else:
            # Insert new user
            ins = """
        INSERT INTO customer (
            email, name, password, building_number, street,
            city, state, phone_number, passport_number, passport_expiration,
            passport_country, date_of_birth
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s
        )
    """
        cursor.execute(ins, (
            email, name, password, building_number, street,
            city, state, phone_number, passport_number, passport_expiration,
            passport_country, date_of_birth
        ))
        flash('Ticket purchased successfully!', 'success')
        conn2.commit()
        # cursor.close()
        return render_template('index.html')
    
    except mysql.connector.errors.OperationalError as e:
        # Catch the OperationalError and redirect to the error page
        print(f"Database error: {e}")
        return redirect(url_for('error'))

#Authenticates the register for Booking Agent
@app.route('/registerAuthBookingAgentsecond', methods=['POST'])
def registerAuthBookingAgentsecond():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        booking_agent_id = request.form.get('booking_agent_id')

        cursor = conn2.cursor()

        # Check if agent already exists
        query = "SELECT * FROM booking_agent WHERE email = %s"
        cursor.execute(query, (email,))
        data = cursor.fetchone()

        if data:
            error = "This booking agent already exists"
            return render_template('registerforBookingagentsecond.html', error=error)
        else:
            ins = """
                INSERT INTO booking_agent (
                    email, password, booking_agent_id
                ) VALUES (%s, %s, %s)
            """
            cursor.execute(ins, (email, password, booking_agent_id))
            conn2.commit()
            # cursor.close()
            return render_template('index.html')
        
    except mysql.connector.errors.OperationalError as e:
        # Catch the OperationalError and redirect to the error page
        print(f"Database error: {e}")
        return redirect(url_for('error'))
    
@app.route('/registerAuthBookingAgentfirst', methods=['POST'])
def registerAuthBookingAgentfirst():
    return render_template('registerforBookingagentfirst.html')



#Authenticates the register for Staff
@app.route('/registerAuthStaff', methods=['POST'])
def registerAuthStaff():
    username = request.form.get('username')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    date_of_birth = request.form.get('date_of_birth')
    airline_name = request.form.get('airline_name')

    cursor = conn2.cursor()

    query = "SELECT * FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username,))
    data = cursor.fetchone()

    if data:
        error = "This staff member already exists"
        return render_template('registerforStaff.html', error=error)
    else:
        ins = """
            INSERT INTO airline_staff (
                username, password, first_name, last_name,
                date_of_birth, airline_name
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(ins, (
            username, password, first_name, last_name,
            date_of_birth, airline_name
        ))
        conn2.commit()
        # cursor.close()
        return render_template('index.html')

@app.route('/home_Customer')
def home_Customer():
    if 'username' not in session:
        return redirect('/login')
	
    ### My Flight Section  ###
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    arrival_airport = request.args.get('arrival_airport')
    departure_airport = request.args.get('departure_airport')
    
    try:
        with conn2.cursor() as cursor:
            # Base query to get customer's flights
            sql = """
                SELECT f.airline_name, f.flight_num, departure_airport, departure_time, 
               arrival_airport, arrival_time, price, status, p.ticket_id
                FROM ticket t join flight f join purchases p                 
                WHERE p.ticket_id=t.ticket_id AND t.flight_num=f.flight_num AND p.customer_email = %s
            """
            now = datetime.now()
            now= now.strftime('%Y-%m-%d')
            params = [session['username']]
            
            # Add filters based on user input
            if start_date:
                sql += " AND f.departure_time >= %s"
                params.append(start_date)
            else:
                sql += " AND f.departure_time >= %s"
                params.append(now)
            if end_date:
                sql += " AND f.departure_time <= %s"
                params.append(end_date + ' 23:59:59')  # Include entire end day
            
            if arrival_airport:
                sql += " AND (f.arrival_airport LIKE %s)"
                params.extend([f"%{arrival_airport}%"])		
            if departure_airport:
                sql += " AND (f.departure_airport LIKE %s)"
                params.extend([f"%{departure_airport}%"])
            
            sql += " ORDER BY f.departure_time ASC"
            
            cursor.execute(sql, params)
            flights = cursor.fetchall()
	
    finally:
        conn2.commit() 
    # finally:
        
    #     conn2.close()

    
    return render_template('home_Customer.html', 
                         username=session['username'],
                         flights=flights)

@app.route('/home_Customer_Search')
def home_Customer_Search():
    if 'username' not in session:
        return redirect('/login')
	
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    arrival_airport = request.args.get('arrival_airport')
    departure_airport = request.args.get('departure_airport')

    try:
        with conn2.cursor() as cursor:
            # Base query to get customer's flights
            sql = """
                SELECT f.airline_name, f.flight_num, departure_airport, departure_time, 
               arrival_airport, arrival_time, price, status
                FROM flight f           
                Where f.departure_time>=%s   
     
            """
            now = datetime.now()
            now= now.strftime('%Y-%m-%d')
            params = [now]
            
            # Add filters based on user input
            if start_date:
                sql += " AND f.departure_time >= %s"
                params.append(start_date)
            if end_date:
                sql += " AND f.departure_time <= %s"
                params.append(end_date + ' 23:59:59')  # Include entire end day
            if arrival_airport:
                sql += " AND (f.arrival_airport LIKE %s)"
                params.extend([f"%{arrival_airport}%"])		
            if departure_airport:
                sql += " AND (f.departure_airport LIKE %s)"
                params.extend([f"%{departure_airport}%"])
            
            sql += " ORDER BY f.departure_time ASC"
            
            cursor.execute(sql, params)
            flights2 = cursor.fetchall()

	
    finally:
        conn2.commit() 
    # finally:
        
    #     conn2.close()

    
    return render_template('home_Customer.html', 
                         username=session['username'],
                         flights2=flights2)

@app.route('/home_Customer_Purchase', methods=['POST'])
def home_Customer_Purchase():
    if 'username' not in session:
        return redirect('/login')
    
    # Get selected flight data
    selected_flight = request.form.get('selected_flight')
    
    if selected_flight is not None:
        airline_name, flight_num = selected_flight.split('_')
    
        with conn2.cursor() as cursor:
            print("try",flight_num)
             
            # Check if flight is full
            cursor.execute("""
            SELECT 
                airline_name, 
                flight_num, 
                COUNT(ticket_id) as sold_seats
            FROM 
                ticket
            WHERE 
                airline_name = %s AND flight_num = %s
            GROUP BY 
                airline_name, flight_num
        """, (airline_name, flight_num))
            
            flight_data = cursor.fetchone()
            if flight_data is None:
                sold_seats=0
            else:           
                sold_seats = flight_data[2] 

            cursor.execute(""" Select airplane_id
                            From flight
                            Where airline_name=%s AND flight_num=%s
                            """,(airline_name, flight_num))
            airplane_data=cursor.fetchone()
            airplane_id=airplane_data[0]
            
            cursor.execute(""" Select seats
                            From airplane
                            Where airplane_id=%s
                            """,(airplane_id,))
            seats_data=cursor.fetchone()
            total_seats=seats_data[0]
            print("if")
            error=None


            
            if sold_seats >= total_seats:
                print("full")
                error='This flight is already full. Cannot purchase ticket.'

            else:
                print(flight_num)
                # Create ticket
                con = True
                while con:
                    ticket_id = random.randint(1000, 9999)  # Adjust range as needed
                    cursor.execute("SELECT 1 FROM ticket WHERE ticket_id = %s", (ticket_id,))
                    if cursor.fetchone() is None:
                        con = False
                
                cursor.execute("""
                    INSERT INTO ticket (ticket_id, airline_name, flight_num) 
                    VALUES (%s, %s, %s)
                """, (ticket_id, airline_name, flight_num))
                
                # Record purchase
                email = session['username']
                now = datetime.now()
                now = now.strftime('%Y-%m-%d')
                cursor.execute("""
                    INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) 
                    VALUES (%s, %s, %s, %s)
                """, (ticket_id, email, None, now))

                conn2.commit()
                flash('Ticket purchased successfully!', 'success')
                        
    return render_template('home_Customer.html',error=error)

@app.route('/home_Customer_Spending',methods=['GET'])
def home_Customer_Spending():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get date range parameters (default to last year)
   # Get current date (as datetime object)
    end_date1 = datetime.now()

    # Subtract 180 days from the current date to get start_date
    start_date1 = end_date1 - timedelta(days=180)

    # If you need end_date and start_date as strings in '%Y-%m-%d' format, use strftime()
    end_date = end_date1.strftime('%Y-%m-%d')
    start_date = start_date1.strftime('%Y-%m-%d')

    start_datess=request.args.get('start_datess')
    end_datess=request.args.get('end_datess')
    if start_datess:
        start_date = start_datess
    if end_datess:
        end_date = end_datess

    custom_range = 'start_datess' in request.args or 'end_datess' in request.args
    
    
    with conn2.cursor(dictionary=True) as cursor:
        # Get total spending for period
        cursor.execute( """
                SELECT sum(f.price) as total_spent
                FROM ticket t join flight f join purchases p                 
                WHERE p.ticket_id=t.ticket_id AND t.flight_num=f.flight_num AND p.customer_email = %s
                  AND p.purchase_date >= %s    AND p.purchase_date <= %s       """
            
           # AND p.purchase_date BETWEEN %s AND %s
        , (session['username'],start_date, end_date))#start_date, 
        total_result = cursor.fetchone()
        print(total_result)
        print('total_spent',total_result['total_spent'])
        total_spent = total_result['total_spent'] if total_result['total_spent'] else 0

        # Get monthly breakdown
        cursor.execute("""
            SELECT 
                DATE_FORMAT(p.purchase_date, '%Y-%m') as month,
                SUM(price) as amount
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
            WHERE p.customer_email = %s 
            AND p.purchase_date BETWEEN %s AND %s
            GROUP BY DATE_FORMAT(p.purchase_date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 6
        """, (session['username'], start_date, end_date))
        spending_data = cursor.fetchall()
        print(spending_data)
        # Calculate max for chart scaling
        max_spending = max([m['amount'] for m in spending_data]) if spending_data else 1
        avg_monthly = total_spent / len(spending_data) if spending_data else 0
        
    print("Spending route hit. Total spent:", total_spent)
    conn2.commit() 
    return render_template('home_Customer.html',
                         total_spent=total_spent,
                         spending_data=spending_data,
                         max_spending=max_spending,
                         avg_monthly=avg_monthly,
                         custom_range=custom_range,
                         start_date=start_date,
                         end_date=end_date)


@app.route('/home_BookingAgent')
def home_BookingAgent():
    if 'username' not in session:
        return redirect('/login')
	
    ### My Flight Section  ###
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    arrival_airport = request.args.get('arrival_airport')
    departure_airport = request.args.get('departure_airport')
    
    try:
        with conn2.cursor() as cursor:
            # Base query to get customer's flights
            sql = """
                SELECT f.airline_name, f.flight_num, departure_airport, departure_time, 
               arrival_airport, arrival_time, price, status, p.ticket_id, p.customer_email
                FROM ticket t join flight f join purchases p    join booking_agent b            
                WHERE p.ticket_id=t.ticket_id AND t.flight_num=f.flight_num AND b.email = %s AND b.booking_agent_id=p.booking_agent_id
            """
            params = [session['username']]
            print(session['username'])
            
            # Add filters based on user input
            if start_date:
                sql += " AND f.departure_time >= %s"
                params.append(start_date)
            if end_date:
                sql += " AND f.departure_time <= %s"
                params.append(end_date + ' 23:59:59')  # Include entire end day
            if arrival_airport:
                sql += " AND (f.arrival_airport LIKE %s)"
                params.extend([f"%{arrival_airport}%"])		
            if departure_airport:
                sql += " AND (f.departure_airport LIKE %s)"
                params.extend([f"%{departure_airport}%"])
            
            sql += " ORDER BY f.departure_time ASC"
            
            cursor.execute(sql, params)
            flights = cursor.fetchall()
	
    finally:
        conn2.commit() 
   
    return render_template('home_BookingAgent.html', 
                         username=session['username'],
                         flights=flights)

@app.route('/home_BookingAgent_Search')
def home_BookingAgent_Search():
    if 'username' not in session:
        return redirect('/login')
	
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    arrival_airport = request.args.get('arrival_airport')
    departure_airport = request.args.get('departure_airport')
    email=session['username']
    try:
        with conn2.cursor() as cursor:
            # Base query to get customer's flights
            sql = """
                SELECT f.airline_name, f.flight_num, departure_airport, departure_time, 
               arrival_airport, arrival_time, price, status
                FROM flight f join booking_agent_work_for b
                Where b.airline_name=f.airline_name  and b.email=%s
     
            """
            params = [email]
            
            # Add filters based on user input
            if start_date:
                sql += " AND f.departure_time >= %s"
                params.append(start_date)
            if end_date:
                sql += " AND f.departure_time <= %s"
                params.append(end_date + ' 23:59:59')  # Include entire end day
            if arrival_airport:
                sql += " AND (f.arrival_airport LIKE %s)"
                params.extend([f"%{arrival_airport}%"])		
            if departure_airport:
                sql += " AND (f.departure_airport LIKE %s)"
                params.extend([f"%{departure_airport}%"])
            
            sql += " ORDER BY f.departure_time ASC"
            
            cursor.execute(sql, params)
            flights = cursor.fetchall()

    finally:
        pass 
    
    return render_template('home_BookingAgent.html', 
                         username=session['username'],
                         flights2=flights)

@app.route('/home_BookingAgent_Purchase', methods=['POST'])
def home_BookingAgent_Purchase():
    if 'username' not in session:
        return redirect('/login')
    
    # Get selected flight data
    selected_flight = request.form.get('selected_flight')
    customer_email = request.form.get('customer_email')

    if not selected_flight or not customer_email:
        flash('Please select a flight and enter customer email.')
        return redirect(url_for('home_BookingAgent'))
    error=None
    if selected_flight is not None:
        airline_name, flight_num = selected_flight.split('_')
   
        with conn2.cursor() as cursor:
            # Check if flight is full
            cursor.execute("""
            SELECT 
                airline_name, 
                flight_num, 
                COUNT(ticket_id) as sold_seats
            FROM 
                ticket
            WHERE 
                airline_name = %s AND flight_num = %s
            GROUP BY 
                airline_name, flight_num
        """, (airline_name, flight_num))
            
            flight_data = cursor.fetchone()
            if flight_data is None:
                sold_seats=0
            else:           
                sold_seats = flight_data[2] 

            cursor.execute(""" Select airplane_id
                            From flight
                            Where airline_name=%s AND flight_num=%s
                            """,(airline_name, flight_num))
            airplane_data=cursor.fetchone()
            airplane_id=airplane_data[0]
            
            cursor.execute(""" Select seats
                            From airplane
                            Where airplane_id=%s
                            """,(airplane_id,))
            seats_data=cursor.fetchone()
            total_seats=seats_data[0]
            print("if")
            error=None


            
            if sold_seats >= total_seats:
                print("full")
                error='This flight is already full. Cannot purchase ticket.'

            else:
                # Create ticket
                con=True
                while con:
                    ticket_id = random.randint(1000, 9999)  # Adjust range as needed
                    cursor.execute("SELECT 1 FROM ticket WHERE ticket_id = %s", (ticket_id,))
                    if cursor.fetchone() is None:
                        con=False
                cursor.execute("SELECT * FROM customer WHERE email = %s", (customer_email,))
                customer = cursor.fetchone()

                if not customer:
                    error = 'Customer not exist'
                    return render_template('home_BookingAgent.html', error=error)

                #ticket_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO ticket (ticket_id, airline_name,flight_num) 
                    VALUES (%s,%s, %s)
                    """, ( ticket_id,airline_name,flight_num))
                # ticket_id = cursor.lastrowid
                
                # Record purchase
                email=session['username']
                cursor.execute("""
                    SELECT booking_agent_id FROM booking_agent WHERE email = %s
                """, (email,))
                result= cursor.fetchone()
                booking_agent_id=result[0]
            
                now = datetime.now()
                now = now.strftime('%Y-%m-%d')
                cursor.execute("""
                    INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) 
                    VALUES (%s, %s, %s, %s)
                """, (ticket_id,customer_email,booking_agent_id,now))

                conn2.commit()
                flash('Ticket purchased successfully!', 'success')
        
    return render_template('home_BookingAgent.html',error=error)


@app.route('/home_BookingAgent_Commission', methods=['GET'])
def home_BookingAgent_Commission():
    cursor = conn2.cursor(dictionary=True)
    # Get agent ID
    email=session['username']
    if not email:
        return redirect(url_for('login'))
    cursor.execute("""
                SELECT booking_agent_id FROM booking_agent WHERE email = %s
            """, (email,))
    result= cursor.fetchone()
    booking_agent_id=result['booking_agent_id']
    print("bookingagentid",booking_agent_id)

    # Get date range from form or use default 30 days
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=30)
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    # Query commission stats
    cursor.execute("""
        SELECT COUNT(*) AS ticket_count,
               SUM(flight.price * 0.1) AS total_commission,
               AVG(flight.price * 0.1) AS avg_commission
        FROM purchases
        JOIN ticket ON purchases.ticket_id = ticket.ticket_id
        JOIN flight ON ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num
        WHERE purchases.booking_agent_id = %s AND purchase_date BETWEEN %s AND %s
    """, (booking_agent_id, start_date, end_date))

    stats = cursor.fetchone()

    # Separate values
    ticket_count = stats['ticket_count'] or 0
    total_commission = stats['total_commission'] or 0.0
    avg_commission = stats['avg_commission'] or 0.0

    # conn.close()

    return render_template(
        'home_BookingAgent.html',
        ticket_count=ticket_count,
        total_commission=total_commission,
        avg_commission=avg_commission,
        start_date=start_date,
        end_date=end_date
    )

@app.route('/home_BookingAgent_Top', methods=['GET'])
def home_BookingAgent_Top():
    cursor = conn2.cursor(dictionary=True)
    # Get agent ID
    email=session['username']
    if not email:
        return redirect(url_for('login'))
    cursor.execute("""
                SELECT booking_agent_id FROM booking_agent WHERE email = %s
            """, (email,))
    result= cursor.fetchone()
    booking_agent_id=result['booking_agent_id']
    #Top 5 customers by tickets in last 6 months
    six_months_ago = datetime.today().date() - timedelta(days=180)
    cursor.execute("""
        SELECT customer_email AS email, COUNT(*) AS ticket_count
        FROM purchases
        JOIN ticket USING(ticket_id)
        WHERE booking_agent_id = %s AND purchase_date >= %s
        GROUP BY customer_email
        ORDER BY ticket_count DESC
        LIMIT 5
    """, (booking_agent_id, six_months_ago))
    top_by_ticket = cursor.fetchall()

    #Top 5 customers by commission in last year
    one_year_ago = datetime.today().date() - timedelta(days=365)
    cursor.execute("""
        SELECT customer_email AS email, SUM(flight.price * 0.1) AS total_commission
        FROM purchases
        JOIN ticket USING(ticket_id)
        JOIN flight ON ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num
        WHERE booking_agent_id = %s AND purchase_date >= %s
        GROUP BY customer_email
        ORDER BY total_commission DESC
        LIMIT 5
    """, (booking_agent_id, one_year_ago))
    top_by_commission = cursor.fetchall()

    return render_template(
    'home_BookingAgent.html',
    top_customers_tickets=top_by_ticket,
    top_customers_commission=top_by_commission
)

@app.route('/home_AirlineStaff')
def home_AirlineStaff():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return redirect('/login')
    
    cursor = conn2.cursor(dictionary=True)
    query = """
        SELECT airline_name, flight_num, departure_airport, departure_time, 
               arrival_airport, arrival_time, price, status
        FROM flight
        WHERE airline_name = %s AND departure_time >= CURDATE() 
        AND departure_time <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ORDER BY departure_time
    """
    cursor.execute(query, (session['airline_name'],))
    flights = cursor.fetchall()
    # cursor.close()
    
    return render_template('home_AirlineStaff.html', 
                         username=session['username'], 
                         airline_name=session['airline_name'],
                         flights=flights)
    


@app.route('/staff_view_flights', methods=['GET', 'POST'])
def staff_view_flights():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return redirect('/login')
    
    cursor = conn2.cursor(dictionary=True)
    
    # Default to next 30 days for GET requests without filters
    start_date = request.form.get('start_date') or request.args.get('start_date')
    end_date = request.form.get('end_date') or request.args.get('end_date')
    departure_airport = request.form.get('departure_airport') or request.args.get('departure_airport')
    arrival_airport = request.form.get('arrival_airport') or request.args.get('arrival_airport')
    
    if not start_date and request.method == 'GET':
        start_date = datetime.now().strftime('%Y-%m-%d')
    if not end_date and request.method == 'GET':
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Build flight query
    sql = """
        SELECT airline_name, flight_num, departure_airport, departure_time, 
               arrival_airport, arrival_time, price, status
        FROM flight
        WHERE airline_name = %s
    """
    params = [session['airline_name']]
    
    if start_date:
        sql += " AND departure_time >= %s"
        params.append(start_date)
    if end_date:
        sql += " AND departure_time <= %s"
        params.append(end_date + ' 23:59:59')
    if departure_airport:
        sql += " AND departure_airport = %s"
        params.append(departure_airport)
    if arrival_airport:
        sql += " AND arrival_airport = %s"
        params.append(arrival_airport)
    
    sql += " ORDER BY departure_time"
    cursor.execute(sql, params)
    flights = cursor.fetchall()
    
    # Get passengers for a specific flight if requested
    passengers = []
    flight_num = request.form.get('flight_num')
    if flight_num:
        cursor.execute("""
            SELECT DISTINCT c.email, c.name
            FROM ticket t
            JOIN purchases p ON t.ticket_id = p.ticket_id
            JOIN customer c ON p.customer_email = c.email
            WHERE t.flight_num = %s AND t.airline_name = %s
        """, (flight_num, session['airline_name']))
        passengers = cursor.fetchall()
    
    # Fetch all airports for filter dropdown
    cursor.execute("SELECT airport_name, airport_city FROM airport ORDER BY airport_name")
    airports = cursor.fetchall()
    
    # cursor.close()
    return render_template('home_AirlineStaff.html', 
                         username=session['username'],
                         airline_name=session['airline_name'],
                         flights=flights,
                         passengers=passengers,
                         flight_num=flight_num,
                         airports=airports,
                         start_date=start_date,
                         end_date=end_date,
                         departure_airport=departure_airport,
                         arrival_airport=arrival_airport)

    
    
    
@app.route('/staff_create_flight', methods=['GET', 'POST'])

def staff_create_flight():
    if 'username' not in session or session['user_type'] != 'airline_staff' or session['permission'] != 'admin':
        return render_template('home_AirlineStaff.html', error="Unauthorized: Admin permission required", username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    if request.method == 'GET':
        cursor = conn2.cursor(dictionary=True)
        cursor.execute("SELECT airplane_id FROM airplane WHERE airline_name = %s", (session['airline_name'],))
        airplanes = cursor.fetchall()
        cursor.execute("SELECT airport_name FROM airport")
        airports = cursor.fetchall()
        # Query for existing flights
        cursor.execute("""
            SELECT flight_num, departure_time, arrival_time
            FROM flight
            WHERE airline_name = %s
            ORDER BY departure_time
        """, (session['airline_name'],))
        flights = cursor.fetchall()
        # cursor.close()
        return render_template('create_flight.html', airplanes=airplanes, airports=airports, flights=flights)
    
    flight_num = request.form['flight_num']
    departure_airport = request.form['departure_airport']
    departure_time = request.form['departure_time']
    arrival_airport = request.form['arrival_airport']
    arrival_time = request.form['arrival_time']
    price = request.form['price']
    status = request.form['status']
    airplane_id = request.form['airplane_id']
    
    cursor = conn2.cursor()
    cursor.execute("SELECT * FROM flight WHERE flight_num = %s AND airline_name = %s", 
                  (flight_num, session['airline_name']))
    if cursor.fetchone():
        # cursor.close()
        return render_template('create_flight.html', error="Flight number already exists")
    
    cursor.execute("""
        INSERT INTO flight (airline_name, flight_num, departure_airport, departure_time, 
                           arrival_airport, arrival_time, price, status, airplane_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (session['airline_name'], flight_num, departure_airport, departure_time, 
          arrival_airport, arrival_time, price, status, airplane_id))
    conn2.commit()
    # cursor.close()
    flash('Flight created successfully!', 'success')
    return redirect('/home_AirlineStaff')




@app.route('/staff_update_status', methods=['GET', 'POST'])
def staff_update_status():
    # if 'username' not in session or session['user_type'] != 'airline_staff' or session['permission'] != 'operator':
    #     return render_template('home_AirlineStaff.html', error="Unauthorized: Operator permission required")
    
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return render_template('home_AirlineStaff.html', error="Unauthorized: Must be airline staff", 
                             username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    # # Verify Operator permission
    # cursor = conn2.cursor(dictionary=True)
    # cursor.execute("SELECT permission_type FROM permission WHERE username = %s AND permission_type = 'Operator'", 
    #                (session['username'],))
    # is_operator = cursor.fetchone()
    # cursor.close()
    
    if session['permission'] != 'operator':
        return render_template('home_AirlineStaff.html', error="Unauthorized: Operator permission required", 
                             username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    if request.method == 'GET':
        cursor = conn2.cursor(dictionary=True)
        cursor.execute("""
            SELECT flight_num, departure_time, arrival_time, price, status, 
                   airline_name, airplane_id, departure_airport, arrival_airport
            FROM flight 
            WHERE airline_name = %s
            ORDER BY departure_time
        """, (session['airline_name'],))
        flights = cursor.fetchall()
        # cursor.close()
        return render_template('update_status.html', flights=flights, session=session)
    
    if request.method == 'POST':
        flight_num = request.form.get('flight_num')
        new_status = request.form.get('status')
        
        if not flight_num or not new_status:
            return render_template('update_status.html', error="Please select a flight and a new status", 
                                 flights=flights, session=session)
        
        cursor = conn2.cursor(dictionary=True)
        # Validate flight exists and belongs to the airline
        cursor.execute("""
            SELECT * FROM flight 
            WHERE flight_num = %s AND airline_name = %s
        """, (flight_num, session['airline_name']))
        flight = cursor.fetchone()
        
        if not flight:
            # cursor.close()
            return render_template('update_status.html', error="Selected flight does not exist", 
                                 flights=flights, session=session)
        
        # Update status
        cursor.execute("""
            UPDATE flight 
            SET status = %s 
            WHERE flight_num = %s AND airline_name = %s
        """, (new_status, flight_num, session['airline_name']))
        conn2.commit()
        # cursor.close()
        
        flash(f"Status of flight {flight_num} updated to {new_status} successfully!", 'success')
        return redirect('/staff_update_status')
    
    
@app.route('/staff_add_airplane', methods=['GET', 'POST'])
def staff_add_airplane():
    if 'username' not in session or session['user_type'] != 'airline_staff' or session['permission'] != 'admin':
        return render_template('home_AirlineStaff.html', error="Unauthorized: Admin permission required", username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    cursor = conn2.cursor(dictionary=True)
    
    if request.method == 'GET':
        cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", 
                      (session['airline_name'],))
        airplanes = cursor.fetchall()
        # cursor.close()
        return render_template('add_airplane.html', airplanes=airplanes)
    
    airplane_id = request.form['airplane_id']
    seats = request.form['seats']
    
    # Check for duplicate airplane ID
    cursor.execute("SELECT * FROM airplane WHERE airplane_id = %s AND airline_name = %s", 
                  (airplane_id, session['airline_name']))
    if cursor.fetchone():
        cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", 
                      (session['airline_name'],))
        airplanes = cursor.fetchall()
        # cursor.close()
        return render_template('add_airplane.html', error="Airplane ID already exists", airplanes=airplanes)
    
    # Insert new airplane
    cursor.execute("""
        INSERT INTO airplane (airline_name, airplane_id, seats)
        VALUES (%s, %s, %s)
    """, (session['airline_name'], airplane_id, seats))
    conn2.commit()
    
    # Fetch updated airplane list
    cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", 
                  (session['airline_name'],))
    airplanes = cursor.fetchall()
    # cursor.close()
    
    flash('Airplane added successfully!', 'success')
    return render_template('add_airplane.html', airplanes=airplanes)

@app.route('/staff_add_airport', methods=['GET', 'POST'])
def staff_add_airport():
    if 'username' not in session or session['user_type'] != 'airline_staff' or session['permission'] != 'admin':
        return render_template('home_AirlineStaff.html', error="Unauthorized: Admin permission required", username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    cursor = conn2.cursor(dictionary=True)
    
    if request.method == 'GET':
        cursor.execute("SELECT airport_name, airport_city FROM airport")
        airports = cursor.fetchall()
        # cursor.close()
        return render_template('add_airport.html', airports=airports)
    
    airport_name = request.form['airport_name']
    airport_city = request.form['airport_city']
    
    # Check for duplicate airport
    cursor.execute("SELECT * FROM airport WHERE airport_name = %s", (airport_name,))
    if cursor.fetchone():
        cursor.execute("SELECT airport_name, airport_city FROM airport")
        airports = cursor.fetchall()
        # cursor.close()
        return render_template('add_airport.html', error="Airport already exists", airports=airports)
    
    # Insert new airport
    cursor.execute("""
        INSERT INTO airport (airport_name, airport_city)
        VALUES (%s, %s)
    """, (airport_name, airport_city))
    conn2.commit()
    
    # Fetch updated airport list
    cursor.execute("SELECT airport_name, airport_city FROM airport")
    airports = cursor.fetchall()
    # cursor.close()
    
    flash('Airport added successfully!', 'success')
    return render_template('add_airport.html', airports=airports)


@app.route('/staff_view_agents', methods=['GET'])
def staff_view_agents():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return redirect('/login')
    
    cursor = conn2.cursor(dictionary=True)
    query_month = """
        SELECT b.email, b.booking_agent_id, COUNT(t.ticket_id) as ticket_count
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN booking_agent b ON p.booking_agent_id = b.booking_agent_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE f.airline_name = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY b.booking_agent_id
        ORDER BY ticket_count DESC
        LIMIT 5
    """
    query_year = """
        SELECT b.email, b.booking_agent_id, COUNT(t.ticket_id) as ticket_count
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN booking_agent b ON p.booking_agent_id = b.booking_agent_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE f.airline_name = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY b.booking_agent_id
        ORDER BY ticket_count DESC
        LIMIT 5
    """
    query_commission = """
        SELECT b.email, b.booking_agent_id, SUM(f.price) * 0.1 as commission
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN booking_agent b ON p.booking_agent_id = b.booking_agent_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE f.airline_name = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY b.booking_agent_id
        ORDER BY commission DESC
        LIMIT 5
    """
    cursor.execute(query_month, (session['airline_name'],))
    agents_month = cursor.fetchall()
    cursor.execute(query_year, (session['airline_name'],))
    agents_year = cursor.fetchall()
    cursor.execute(query_commission, (session['airline_name'],))
    agents_commission = cursor.fetchall()
    cursor.close()
    return render_template('home_AirlineStaff.html', 
                         agents_month=agents_month,
                         agents_year=agents_year,
                         agents_commission=agents_commission,
                         username=session.get('username', ''),
                         airline_name=session.get('airline_name', ''))
    

@app.route('/staff_view_customers', methods=['GET'])
def staff_view_customers():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return redirect('/login')
    
    cursor = conn2.cursor(dictionary=True)
    query = """
        SELECT c.email, c.name, COUNT(t.ticket_id) as ticket_count
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN customer c ON p.customer_email = c.email
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE f.airline_name = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY c.email
        ORDER BY ticket_count DESC
        LIMIT 1
    """
    cursor.execute(query, (session['airline_name'],))
    frequent_customer = cursor.fetchone()
    
    customer_flights = []
    if frequent_customer:
        cursor.execute("""
            SELECT f.airline_name, f.flight_num, f.departure_airport, f.departure_time, 
                   f.arrival_airport, f.arrival_time, f.price, f.status
            FROM ticket t
            JOIN purchases p ON t.ticket_id = p.ticket_id
            JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
            WHERE p.customer_email = %s AND f.airline_name = %s
        """, (frequent_customer['email'], session['airline_name']))
        customer_flights = cursor.fetchall()
    
    cursor.close()
    return render_template('home_AirlineStaff.html', 
                         frequent_customer=frequent_customer,
                         customer_flights=customer_flights,
                         username=session.get('username', ''),
                         airline_name=session.get('airline_name', ''))
    
    
@app.route('/staff_reports', methods=['GET', 'POST'])
def staff_reports():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return redirect('/login')
    
    # Handle date range from form (POST) or URL (GET)
    range_type = request.form.get('range_type') or request.args.get('range_type')
    start_date = request.form.get('start_date') or request.args.get('start_date')
    end_date = request.form.get('end_date') or request.args.get('end_date')
    
    # Set preset date ranges
    today = datetime.now().date()
    if range_type == 'last_month':
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif range_type == 'last_year':
        start_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    else:
        # Default to last year if no dates provided
        start_date = start_date or (today - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = end_date or today.strftime('%Y-%m-%d')
    
    # Validate dates
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        if start_date > end_date:
            start_date, end_date = end_date, start_date
    except ValueError:
        start_date = (today - timedelta(days=365)).date()
        end_date = today
    
    cursor = conn2.cursor(dictionary=True)
    
    # Total tickets query
    query_total = """
        SELECT COUNT(t.ticket_id) as total_tickets
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE f.airline_name = %s AND p.purchase_date BETWEEN %s AND %s
    """
    cursor.execute(query_total, (session['airline_name'], start_date, end_date))
    total_tickets = cursor.fetchone()['total_tickets']
    
    # Month-wise tickets for bar chart
    query_tickets = """
        SELECT DATE_FORMAT(p.purchase_date, '%Y-%m') as month, COUNT(t.ticket_id) as ticket_count
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE f.airline_name = %s AND p.purchase_date BETWEEN %s AND %s
        GROUP BY DATE_FORMAT(p.purchase_date, '%Y-%m')
        ORDER BY month
    """
    cursor.execute(query_tickets, (session['airline_name'], start_date, end_date))
    ticket_data = cursor.fetchall()
    
    # Prepare chart data
    chart_labels = [data['month'] for data in ticket_data]
    chart_values = [data['ticket_count'] for data in ticket_data]
    
    cursor.close()
    
    return render_template('staff_reports.html',
                         ticket_data=ticket_data,
                         total_tickets=total_tickets,
                         chart_labels=json.dumps(chart_labels),
                         chart_values=json.dumps(chart_values),
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'),
                         range_type=range_type)


@app.route('/staff_revenue', methods=['GET'])
def staff_revenue():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return redirect('/login')
    
    cursor = conn2.cursor(dictionary=True)
    today = datetime.now().date()
    last_month_start = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    last_year_start = (today - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # Revenue query template
    query_revenue = """
        SELECT 
            SUM(CASE WHEN p.booking_agent_id IS NULL THEN f.price ELSE 0 END) as direct_revenue,
            SUM(CASE WHEN p.booking_agent_id IS NOT NULL THEN f.price ELSE 0 END) as indirect_revenue
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE f.airline_name = %s AND p.purchase_date BETWEEN %s AND %s
    """
    
    # Last month revenue
    cursor.execute(query_revenue, (session['airline_name'], last_month_start, end_date))
    month_revenue = cursor.fetchone()
    month_direct = float(month_revenue['direct_revenue'] or 0)
    month_indirect = float(month_revenue['indirect_revenue'] or 0)
    month_total = month_direct + month_indirect
    
    # Last year revenue
    cursor.execute(query_revenue, (session['airline_name'], last_year_start, end_date))
    year_revenue = cursor.fetchone()
    year_direct = float(year_revenue['direct_revenue'] or 0)
    year_indirect = float(year_revenue['indirect_revenue'] or 0)
    year_total = year_direct + year_indirect
    
    cursor.close()
    
    # Chart data
    month_chart_data = {
        'labels': ['Direct Sales', 'Indirect Sales'],
        'values': [month_direct, month_indirect]
    }
    year_chart_data = {
        'labels': ['Direct Sales', 'Indirect Sales'],
        'values': [year_direct, year_indirect]
    }
    
    return render_template('staff_revenue.html',
                         month_direct=month_direct,
                         month_indirect=month_indirect,
                         month_total=month_total,
                         year_direct=year_direct,
                         year_indirect=year_indirect,
                         year_total=year_total,
                         month_chart_data=json.dumps(month_chart_data),
                         year_chart_data=json.dumps(year_chart_data),
                         airline_name=session['airline_name'])
    
    
@app.route('/staff_top_destinations', methods=['GET'])
def staff_top_destinations():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return redirect('/login')
    
    cursor = conn2.cursor(dictionary=True)
    today = datetime.now().date()
    last_3_months_start = (today - timedelta(days=90)).strftime('%Y-%m-%d')
    last_year_start = (today - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    query_3months = """
        SELECT a.airport_city, COUNT(t.ticket_id) as ticket_count
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        JOIN airport a ON f.arrival_airport = a.airport_name
        WHERE f.airline_name = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
        GROUP BY a.airport_city
        ORDER BY ticket_count DESC
        LIMIT 3
    """
    query_year = """
        SELECT a.airport_city, COUNT(t.ticket_id) as ticket_count
        FROM ticket t
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        JOIN airport a ON f.arrival_airport = a.airport_name
        WHERE f.airline_name = %s AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY a.airport_city
        ORDER BY ticket_count DESC
        LIMIT 3
    """
    
    cursor.execute(query_3months, (session['airline_name'],))
    destinations_3months = cursor.fetchall()
    cursor.execute(query_year, (session['airline_name'],))
    destinations_year = cursor.fetchall()
    cursor.close()
    
    return render_template('home_AirlineStaff.html',
                         destinations_3months=destinations_3months,
                         destinations_year=destinations_year,
                         airline_name=session['airline_name'],
                         last_3_months_start=last_3_months_start,
                         end_date=end_date,
                         last_year_start=last_year_start,
                         username=session.get('username', ''))
    

@app.route('/staff_grant_permission', methods=['GET', 'POST'])
def staff_grant_permission():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return render_template('home_AirlineStaff.html', error="Unauthorized: Must be airline staff", username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    # Verify Admin permission
    cursor = conn2.cursor(dictionary=True)
    cursor.execute("SELECT permission_type FROM permission WHERE username = %s AND permission_type = 'Admin'", 
                   (session['username'],))
    is_admin = cursor.fetchone()
    cursor.close()
    
    if not is_admin:
        return render_template('home_AirlineStaff.html', error="Unauthorized: Admin permission required", username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    if request.method == 'GET':
        cursor = conn2.cursor(dictionary=True)
        cursor.execute("""
            SELECT username, first_name, last_name, 
                   (SELECT permission_type FROM permission p WHERE p.username = s.username) as permission_type
            FROM airline_staff s
            WHERE airline_name = %s AND username != %s
        """, (session['airline_name'], session['username']))
        staff = cursor.fetchall()
        cursor.close()
        return render_template('grant_permission.html', staff=staff, airline_name=session['airline_name'])
    
    staff_username = request.form.get('staff_username')
    permission_type = request.form.get('permission_type')
    
    if not staff_username or permission_type not in ['Admin', 'Operator', 'none']:
        flash('Invalid input: Please select a valid staff member and permission type.', 'error')
        return redirect('/staff_grant_permission')
    
    # Verify staff exists and is in the same airline
    cursor = conn2.cursor(dictionary=True)
    cursor.execute("SELECT username FROM airline_staff WHERE username = %s AND airline_name = %s", 
                   (staff_username, session['airline_name']))
    if not cursor.fetchone():
        cursor.close()
        flash('Error: Selected staff member does not exist or is not in your airline.', 'error')
        return redirect('/staff_grant_permission')
    
    # Update permission
    cursor.execute("DELETE FROM permission WHERE username = %s", (staff_username,))
    if permission_type != 'none':
        cursor.execute("""
            INSERT INTO permission (username, permission_type)
            VALUES (%s, %s)
        """, (staff_username, permission_type))
    conn2.commit()
    cursor.close()
    
    flash(f'Permission updated successfully for {staff_username}!', 'success')
    return redirect('/home_AirlineStaff')

@app.route('/staff_add_agent', methods=['GET', 'POST'])
def staff_add_agent():
    if 'username' not in session or session['user_type'] != 'airline_staff':
        return render_template('home_AirlineStaff.html', error="Unauthorized: Must be airline staff", username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    # Verify Admin permission
    cursor = conn2.cursor(dictionary=True)
    cursor.execute("SELECT permission_type FROM permission WHERE username = %s AND permission_type = 'Admin'", 
                   (session['username'],))
    is_admin = cursor.fetchone()
    cursor.close()
    
    if not is_admin:
        return render_template('home_AirlineStaff.html', error="Unauthorized: Admin permission required", username=session.get('username', ''), airline_name=session.get('airline_name', ''))
    
    if request.method == 'GET':
        cursor = conn2.cursor(dictionary=True)
        cursor.execute("""
            SELECT ba.email, ba.booking_agent_id
            FROM booking_agent ba
            JOIN booking_agent_work_for wf ON ba.email = wf.email
            WHERE wf.airline_name = %s
        """, (session['airline_name'],))
        agents = cursor.fetchall()
        cursor.close()
        return render_template('add_agent.html', agents=agents, airline_name=session['airline_name'])
    
    email = request.form.get('email')
    
    # Validate email format
    if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        flash('Invalid email format.', 'error')
        return redirect('/staff_add_agent')
    
    cursor = conn2.cursor(dictionary=True)
    
    # Check if email exists in booking_agent
    cursor.execute("SELECT email FROM booking_agent WHERE email = %s", (email,))
    agent_exists = cursor.fetchone()
    if not agent_exists:
        cursor.close()
        flash('Error: Booking agent email not found.', 'error')
        return redirect('/staff_add_agent')
    
    # Check if agent is already added for this airline
    cursor.execute("SELECT email FROM booking_agent_work_for WHERE email = %s AND airline_name = %s", 
                   (email, session['airline_name']))
    already_added = cursor.fetchone()
    if already_added:
        cursor.close()
        flash('Error: Booking agent is already added for this airline.', 'error')
        return redirect('/staff_add_agent')
    
    # Add agent to booking_agent_work_for
    cursor.execute("""
        INSERT INTO booking_agent_work_for (email, airline_name)
        VALUES (%s, %s)
    """, (email, session['airline_name']))
    conn2.commit()
    cursor.close()
    
    flash(f'Booking agent {email} added successfully!', 'success')
    return redirect('/staff_add_agent')



@app.route('/logout')
def logout():
    # conn2.close() 
    session.pop('username')
    return redirect('/')
	
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
