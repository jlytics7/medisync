from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="miranda7282004",
            database="pharmacy_db"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(" Database connection failed:", e)
        return None

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        category = request.form.get('category')
        idnumber = request.form.get('idnumber')

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "error")
            return redirect(url_for('login'))

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE category = %s AND idnumber = %s", (category, idnumber))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
        
            session['username'] = user['username']
            session['role'] = user['category']  
            return redirect(url_for('dashboard', username=user['username']))
        else:
            flash("Invalid category or ID number.", "error")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        category = request.form.get('category')
        idnumber = request.form.get('idnumber')

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "error")
            return redirect(url_for('register'))

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE idnumber = %s", (idnumber,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("This ID number is already registered.", "error")
        else:
            cursor.execute(
                "INSERT INTO users (username, category, idnumber) VALUES (%s, %s, %s)",
                (username, category, idnumber)
            )
            conn.commit()
            flash("Registration successful! You can now log in.", "success")

        cursor.close()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard/<username>')
def dashboard(username):
    conn = get_db_connection()   
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('login'))

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()

    for med in medicines:
        if isinstance(med['expiry_date'], str):
            try:
                med['expiry_date'] = datetime.strptime(med['expiry_date'], "%Y-%m-%d").date()
            except:
                med['expiry_date'] = None

    cursor.execute("SELECT COUNT(*) AS total_meds FROM medicines")
    total_meds = cursor.fetchone()['total_meds']

    cursor.execute("SELECT COUNT(*) AS low_stock FROM medicines WHERE quantity < 10")
    low_stock = cursor.fetchone()['low_stock']

    cursor.execute("SELECT COUNT(*) AS out_of_stock FROM medicines WHERE quantity = 0")
    out_of_stock = cursor.fetchone()['out_of_stock']

    cursor.execute("SELECT COUNT(*) AS expired_meds FROM medicines WHERE expiry_date < CURDATE()")
    expired_meds = cursor.fetchone()['expired_meds']

    cursor.execute("SELECT * FROM medicines WHERE quantity < 10 OR expiry_date < CURDATE()")
    low_expired_meds = cursor.fetchall()

    cursor.execute("""
        SELECT p.id, m.medicine_name, p.quantity, p.total_price, p.purchase_datetime
        FROM purchases p
        JOIN medicines m ON p.medicine_id = m.id
        WHERE DATE(p.purchase_datetime) = CURDATE()
        ORDER BY p.purchase_datetime DESC
    """)
    recent_purchases = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        username=username,
        medicines=medicines,
        total_meds=total_meds,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        expired_meds=expired_meds,
        low_expired_meds=low_expired_meds,
        recent_purchases=recent_purchases,
        current_date=date.today(),
        role=session.get('role')
    )


@app.route('/inventory/<username>')
def inventory(username):
    search_query = request.args.get('search', '')  

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('login'))

    cursor = conn.cursor(dictionary=True)

    if search_query:

        cursor.execute(
            "SELECT * FROM medicines WHERE medicine_name LIKE %s OR category LIKE %s",
            (f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor.execute("SELECT * FROM medicines")

    medicines = cursor.fetchall()

    for med in medicines:
        if isinstance(med['expiry_date'], str):
            try:
                med['expiry_date'] = datetime.strptime(med['expiry_date'], "%Y-%m-%d").date()
            except:
                med['expiry_date'] = None

    cursor.execute("SELECT COUNT(*) AS total_meds FROM medicines")
    total_meds = cursor.fetchone()['total_meds']

    cursor.execute("SELECT COUNT(*) AS low_stock FROM medicines WHERE quantity < 10")
    low_stock = cursor.fetchone()['low_stock']

    cursor.execute("SELECT COUNT(*) AS out_of_stock FROM medicines WHERE quantity = 0")
    out_of_stock = cursor.fetchone()['out_of_stock']

    cursor.execute("SELECT COUNT(*) AS expired_meds FROM medicines WHERE expiry_date < CURDATE()")
    expired_meds = cursor.fetchone()['expired_meds']

    cursor.close()
    conn.close()

    return render_template(
        'inventory.html',
        username=username,
        medicines=medicines,
        total_meds=total_meds,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        expired_meds=expired_meds,
        current_date=date.today(),
        role=session.get('role')
    )

@app.route('/add_medicine/<username>', methods=['GET', 'POST'])
@app.route('/add_medicine/<username>/<int:medicine_id>', methods=['GET', 'POST'])
def add_medicine(username, medicine_id=None):
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('login'))

    cursor = conn.cursor(dictionary=True)
    medicine = None

    if medicine_id:
        cursor.execute("SELECT * FROM medicines WHERE id = %s", (medicine_id,))
        medicine = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['medicine_name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']
        expiry_date = request.form['expiry_date']

        if medicine:
            cursor.execute("""
                UPDATE medicines
                SET medicine_name = %s, category = %s, price = %s, quantity = %s, expiry_date = %s
                WHERE id = %s
            """, (name, category, price, quantity, expiry_date, medicine_id))
            flash(f"{name} updated successfully!", "success")
        else:
            cursor.execute("""
                INSERT INTO medicines (medicine_name, category, price, quantity, expiry_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, category, price, quantity, expiry_date))
            flash(f"{name} added successfully!", "success")

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('add_medicine', username=username))

    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('add_medicine.html', username=username, medicines=medicines, medicine=medicine, role=session.get('role'))


@app.route('/delete_medicine/<username>/<int:medicine_id>', methods=['POST'])
def delete_medicine(username, medicine_id):
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('add_medicine', username=username))

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT medicine_name FROM medicines WHERE id = %s", (medicine_id,))
    med = cursor.fetchone()

    if not med:
        flash("Medicine not found.", "error")
    else:
        cursor.execute("SELECT COUNT(*) AS cnt FROM purchases WHERE medicine_id = %s", (medicine_id,))
        count = cursor.fetchone()['cnt']

        if count > 0:
            flash(f"Cannot delete '{med['medicine_name']}' because it has purchase records.", "error")
        else:
            cursor.execute("DELETE FROM medicines WHERE id = %s", (medicine_id,))
            conn.commit()
            flash(f"{med['medicine_name']} deleted successfully!", "success")

    cursor.close()
    conn.close()
    return redirect(url_for('add_medicine', username=username))


@app.route('/purchase/<username>', methods=['GET', 'POST'])
def purchase(username):
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('login'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, medicine_name, quantity, price FROM medicines WHERE quantity > 0")
    medicines = cursor.fetchall()

    if request.method == 'POST':
        medicine_id = request.form.get('medicine_id')
        quantity = int(request.form.get('quantity'))

        cursor.execute("SELECT price, quantity, medicine_name FROM medicines WHERE id = %s", (medicine_id,))
        med = cursor.fetchone()

        if not med:
            flash()
        elif quantity > med['quantity']:
            flash(f"Only {med['quantity']} of '{med['medicine_name']}' available.", "error")
        else:
            total_price = float(med['price']) * quantity
            purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("""
                INSERT INTO purchases (medicine_id, quantity, total_price, purchase_datetime)
                VALUES (%s, %s, %s, %s)
            """, (medicine_id, quantity, total_price, purchase_date))

            cursor.execute("UPDATE medicines SET quantity = quantity - %s WHERE id = %s", (quantity, medicine_id))
            conn.commit()
            flash(f"Purchased {quantity} of '{med['medicine_name']}' successfully!", "success")

        cursor.close()
        conn.close()
        return redirect(url_for('purchase', username=username))

    cursor.close()
    conn.close()
    return render_template('purchase.html', username=username, medicines=medicines, role=session.get('role'))


@app.route('/purchase_history/<username>')
def purchase_history(username):
    search_query = request.args.get('search', '')  

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('login'))

    cursor = conn.cursor(dictionary=True)

    if search_query:
        cursor.execute("""
            SELECT p.id, m.medicine_name, p.quantity, p.total_price, p.purchase_datetime
            FROM purchases p
            JOIN medicines m ON p.medicine_id = m.id
            WHERE m.medicine_name LIKE %s
            ORDER BY p.purchase_datetime DESC
        """, (f"%{search_query}%",))
    else:
        cursor.execute("""
            SELECT p.id, m.medicine_name, p.quantity, p.total_price, p.purchase_datetime
            FROM purchases p
            JOIN medicines m ON p.medicine_id = m.id
            ORDER BY p.purchase_datetime DESC
        """)

    purchases = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('purchase_history.html', username=username, purchases=purchases, role=session.get('role'))


if __name__ == "__main__":
    app.run(debug=True)
    