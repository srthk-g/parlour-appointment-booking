import sqlite3

DB_NAME = "database.db"


# ==========================
# CONNECT
# ==========================
def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================
# INIT DATABASE
# ==========================
def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # USERS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'customer'
        )
        """)

        # SERVICES (UNIQUE NAME)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price INTEGER,
            duration INTEGER
        )
        """)

        # APPOINTMENTS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'Pending',
            notes TEXT
        )
        """)


# ==========================
# USERS
# ==========================
def create_user(name, email, password):
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_user(email, password):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()


# ==========================
# SERVICES
# ==========================
def add_service(name, price, duration):
    with get_connection() as conn:
        cursor = conn.cursor()

        # 🔒 HARD CHECK BEFORE INSERT
        existing = cursor.execute(
            "SELECT id FROM services WHERE name = ?",
            (name,)
        ).fetchone()

        if existing:
            return False

        cursor.execute(
            "INSERT INTO services (name, price, duration) VALUES (?, ?, ?)",
            (name, price, duration)
        )

        return True


def get_services():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM services").fetchall()


def delete_service(service_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM services WHERE id=?", (service_id,))


# ==========================
# APPOINTMENTS
# ==========================
def create_appointment(user_id, service, date, time, notes):
    with get_connection() as conn:
        cursor = conn.cursor()

        # PREVENT DOUBLE BOOKING
        existing = cursor.execute(
            "SELECT id FROM appointments WHERE date=? AND time=?",
            (date, time)
        ).fetchone()

        if existing:
            return False

        cursor.execute("""
            INSERT INTO appointments (user_id, service, date, time, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, service, date, time, notes))

        return True


def get_user_appointments(user_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM appointments WHERE user_id=?",
            (user_id,)
        ).fetchall()


def get_all_appointments():
    with get_connection() as conn:
        return conn.execute("""
            SELECT a.*, u.name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
        """).fetchall()


def update_appointment_status(appt_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE appointments SET status='Completed' WHERE id=?",
            (appt_id,)
        )


# ==========================
# DASHBOARD
# ==========================
def get_dashboard_stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
        pending = conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE status='Pending'"
        ).fetchone()[0]
        completed = conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE status='Completed'"
        ).fetchone()[0]

        return total, pending, completed


def get_daily_bookings():
    with get_connection() as conn:
        data = conn.execute("""
            SELECT date, COUNT(*) as count
            FROM appointments
            GROUP BY date
            ORDER BY date
        """).fetchall()

        labels = [row['date'] for row in data]
        values = [row['count'] for row in data]

        return labels, values

def seed_services():
    with get_connection() as conn:
        cursor = conn.cursor()

        # check if any services exist
        existing = cursor.execute("SELECT COUNT(*) FROM services").fetchone()[0]

        if existing == 0:
            cursor.executemany("""
                INSERT INTO services (name, price, duration)
                VALUES (?, ?, ?)
            """, [
                ("Hair Styling", 500, 60),
                ("Facial", 800, 75),
                ("Makeup", 1500, 90),
                ("Manicure", 600, 60)
            ])

def seed_admin():
    with get_connection() as conn:
        cursor = conn.cursor()

        # check if admin exists
        existing = cursor.execute(
            "SELECT * FROM users WHERE role='admin'"
        ).fetchone()

        if not existing:
            print("Creating admin user...")  # debug

            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, ("Admin", "admin@gmail.com", "1234", "admin"))
