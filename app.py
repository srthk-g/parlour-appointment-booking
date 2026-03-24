from flask import Flask, render_template, request, redirect, session, flash
from models.db import *

app = Flask(__name__)
app.secret_key = "secret123"

# INIT DATABASE
init_db()
seed_services()  
seed_admin() 


# ==========================
# HOME
# ==========================
@app.route('/')
def home():
    return render_template('index.html')


# ==========================
# REGISTER
# ==========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect('/register')

        try:
            create_user(name, email, password)
            flash("Account created successfully!", "success")
            return redirect('/login')
        except:
            flash("User already exists", "danger")
            return redirect('/register')

    return render_template('register.html')


# ==========================
# LOGIN
# ==========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user(email, password)

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']

            if user['role'] == 'admin':
                return redirect('/dashboard')
            else:
                return redirect('/')
        else:
            flash("Incorrect email or password", "danger")

    return render_template('login.html')


# ==========================
# LOGOUT
# ==========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==========================
# SERVICES (USER VIEW)
# ==========================
@app.route('/services')
def services():
    services = get_services()
    return render_template('services.html', services=services)


# ==========================
# BOOK APPOINTMENT
# ==========================
@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        return redirect('/login')

    services = get_services()

    if request.method == 'POST':
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        notes = request.form['notes']

        success = create_appointment(
            session['user_id'], service, date, time, notes
        )

        if not success:
            flash("Slot already booked!", "danger")
            return redirect('/book')

        flash("Appointment booked successfully!", "success")
        return redirect('/my_appointments')

    return render_template('book.html', services=services)
# ==========================
# MY APPOINTMENTS
# ==========================
@app.route('/my_appointments')
def my_appointments():
    if 'user_id' not in session:
        return redirect('/login')

    appointments = get_user_appointments(session['user_id'])
    return render_template('my_appointments.html', appointments=appointments)


# ==========================
# ADMIN DASHBOARD
# ==========================
@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return redirect('/')

    total, pending, completed = get_dashboard_stats()
    labels, values = get_daily_bookings()

    return render_template(
        'dashboard.html',
        total_bookings=total,
        pending_count=pending,
        completed_count=completed,
        labels=labels,
        values=values
    )

# ==========================
# MANAGE APPOINTMENTS
# ==========================
@app.route('/manage_appointments')
def manage_appointments():
    if session.get('role') != 'admin':
        return redirect('/')

    appointments = get_all_appointments()
    return render_template('manage_appointments.html', appointments=appointments)


@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    update_appointment_status(id)
    return redirect('/manage_appointments')

# ==========================
# MANAGE SERVICES
# ==========================
@app.route('/manage_services')
def manage_services():
    if session.get('role') != 'admin':
        return redirect('/')

    services = get_services()
    return render_template('manage_services.html', services=services)


@app.route('/add_service', methods=['POST'])
def add_service_route():
    name = request.form['name']
    price = request.form['price']
    duration = request.form['duration']

    add_service(name, price, duration)
    flash("Service added successfully", "success")

    return redirect('/manage_services')


@app.route('/delete_service/<int:id>', methods=['POST'])
def delete_service_route(id):
    delete_service(id)
    flash("Service deleted", "danger")

    return redirect('/manage_services')


# ==========================
# RUN APP
# ==========================
if __name__ == '__main__':
    app.run(debug=True)
