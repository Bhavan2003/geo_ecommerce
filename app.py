from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

# ✅ MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # your MySQL username
app.config['MYSQL_PASSWORD'] = 'Bhavan@2003'  # your MySQL password
app.config['MYSQL_DB'] = 'geo_db'

mysql = MySQL(app)

# ✅ Home route
@app.route('/')
def home():
    return render_template('index.html')


# ✅ Register new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({'status': 'error', 'message': 'Username already exists'})

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})


# ✅ Login user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        role = 'admin' if username == 'admin' else 'user'
        cursor.execute("UPDATE users SET status='login', login_time=%s WHERE username=%s", (datetime.now(), username))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success', 'role': role})
    else:
        cursor.close()
        return jsonify({'status': 'error'})


# ✅ Logout user
@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    username = data['username']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET status='logout', logout_time=%s WHERE username=%s", (datetime.now(), username))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})



# ✅ Admin – View all users
@app.route('/admin/users', methods=['GET'])
def admin_users():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username, role, status, login_time, logout_time FROM users")
    result = cursor.fetchall()
    cursor.close()

    # Convert tuples → JSON-friendly list
    users = []
    for row in result:
        users.append({
            'username': row[0],
            'role': row[1],
            'status': row[2],
            'login_time': str(row[3]) if row[3] else None,
            'logout_time': str(row[4]) if row[4] else None
        })

    return jsonify(users)


# ✅ Admin – Delete user
@app.route('/admin/delete', methods=['POST'])
def delete_user():
    data = request.get_json()
    username = data['username']

    # Prevent admin deletion
    if username == 'admin':
        return jsonify({'status': 'error', 'message': "Can't delete admin"})

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE username=%s", (username,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
