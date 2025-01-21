from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import datetime

app = Flask(__name__)

# Конфигурация базы данных
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Укажите ваш пароль, если установлен
app.config['MYSQL_DB'] = 'restaurant'
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Конфигурация сессий
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

mysql = MySQL(app)

# Главная страница
@app.route('/')
def home():
    return render_template('index.html')

# Страница меню
@app.route('/menu')
def menu():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM menu_items")
    menu_items = cursor.fetchall()
    return render_template('menu.html', menu=menu_items)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        phone = request.form.get('phone')
        reservation_date = request.form.get('reservation_date')
        table_number = request.form.get('table_number')

        if not all([customer_name, phone, reservation_date, table_number]):
            return render_template('booking.html', error="All fields are required!")

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO reservations (customer_name, phone, reservation_date, table_number)
                VALUES (%s, %s, %s, %s)
            """, (customer_name, phone, reservation_date, table_number))
            mysql.connection.commit()
            return render_template('booking.html', success="Your table has been successfully booked!")
        except Exception as e:
            return render_template('booking.html', error="An error occurred while booking. Please try again.")

    return render_template('booking.html')


@app.route('/admin/menu', methods=['GET', 'POST'])
def admin_menu():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM menu_items")
    menu_items = cursor.fetchall()
    return render_template('admin_menu.html', menu=menu_items)


# Админская панель: управление бронированиями
@app.route('/admin/reservations')
def admin_reservations():
    if not session.get('is_admin'):
        return redirect(url_for('login_page'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM reservations")
    reservations = cursor.fetchall()
    return render_template('admin_reservations.html', reservations=reservations)

# Страница логина
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, password, is_admin FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            # Устанавливаем данные пользователя в сессию
            session['user_id'] = user[0]
            session['is_admin'] = user[2]
            return redirect(url_for('admin_menu') if user[2] else url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

# Выход из системы
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # Очищаем сессию
    return redirect(url_for('home'))

@app.route('/admin/menu/add', methods=['POST'])
def add_dish():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    image_url = request.form.get('image_url')
    category = request.form.get('category')  # Получаем категорию

    # Проверяем, выбрана ли категория
    if not category:
        return jsonify({"error": "Category is required!"}), 400

    # Добавляем новое блюдо в базу данных
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO menu_items (name, description, price, image_url, category) VALUES (%s, %s, %s, %s, %s)",
        (name, description, price, image_url, category)
    )
    mysql.connection.commit()
    return jsonify({"message": "Dish added successfully!"})


@app.route('/admin/reservations/delete', methods=['POST'])
def delete_reservation():
    if not session.get('is_admin'):
        return jsonify({"error": "Access forbidden: Admins only"}), 403

    data = request.json
    reservation_id = data.get('id')

    if not reservation_id:
        return jsonify({"error": "Reservation ID is required"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM reservations WHERE id = %s", (reservation_id,))
    mysql.connection.commit()
    return jsonify({"message": "Reservation deleted successfully!"})

@app.route('/admin/reservations/edit', methods=['POST'])
def edit_reservation():
    if not session.get('is_admin'):
        return jsonify({"error": "Access forbidden: Admins only"}), 403

    data = request.json
    reservation_id = data.get('id')
    customer_name = data.get('customer_name')
    phone = data.get('phone')
    reservation_date = data.get('reservation_date')
    table_number = data.get('table_number')

    if not all([reservation_id, customer_name, phone, reservation_date, table_number]):
        return jsonify({"error": "All fields are required"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE reservations
        SET customer_name = %s, phone = %s, reservation_date = %s, table_number = %s
        WHERE id = %s
    """, (customer_name, phone, reservation_date, table_number, reservation_id))
    mysql.connection.commit()
    return jsonify({"message": "Reservation updated successfully!"})

@app.route('/admin/menu/delete/<int:item_id>', methods=['POST'])
def delete_menu_item(item_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM menu_items WHERE id = %s", (item_id,))
    mysql.connection.commit()
    return redirect(url_for('admin_menu'))

# Главный блок для запуска сервера
if __name__ == '__main__':
    app.run(debug=True)
