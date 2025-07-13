# app.py

from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from config import DB_CONFIG

app = Flask(__name__)

def get_db_connection():
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
            "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print("Database connection failed:", e)
        return None

@app.route('/')
def home():
    return "✅ Task Manager API is running"

# ------------------ User APIs ------------------

@app.route('/users', methods=['POST'])
def register_user():
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Users (Username, Email)
            VALUES (?, ?)
        """, (data['username'], data['email']))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Username, Email FROM Users")
    users = []
    for row in cursor.fetchall():
        users.append({
            "userId": row.UserID,
            "username": row.Username,
            "email": row.Email
        })
    conn.close()
    return jsonify(users)

# ------------------ Task APIs ------------------

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Tasks (UserID, Title, Description, Category, Priority, DueDate, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['userId'],
            data['title'],
            data.get('description', ''),
            data.get('category', 'General'),
            data.get('priority', 'Medium'),
            data.get('dueDate', None),
            data.get('status', 'Pending')
        ))
        conn.commit()
        return jsonify({"message": "Task created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT TaskID, UserID, Title, Description, Category, Priority, DueDate, Status, CreatedAt
        FROM Tasks
    """)
    tasks = []
    for row in cursor.fetchall():
        tasks.append({
            "taskId": row.TaskID,
            "userId": row.UserID,
            "title": row.Title,
            "description": row.Description,
            "category": row.Category,
            "priority": row.Priority,
            "dueDate": str(row.DueDate) if row.DueDate else None,
            "status": row.Status,
            "createdAt": str(row.CreatedAt)
        })
    conn.close()
    return jsonify(tasks)

@app.route('/tasks/<int:user_id>', methods=['GET'])
def get_tasks_by_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT TaskID, Title, Description, Category, Priority, DueDate, Status, CreatedAt
        FROM Tasks WHERE UserID = ?
    """, (user_id,))
    tasks = []
    for row in cursor.fetchall():
        tasks.append({
            "taskId": row.TaskID,
            "title": row.Title,
            "description": row.Description,
            "category": row.Category,
            "priority": row.Priority,
            "dueDate": str(row.DueDate) if row.DueDate else None,
            "status": row.Status,
            "createdAt": str(row.CreatedAt)
        })
    conn.close()
    return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Tasks
            SET Title = ?, Description = ?, Category = ?, Priority = ?, DueDate = ?, Status = ?
            WHERE TaskID = ?
        """, (
            data['title'],
            data.get('description', ''),
            data.get('category', 'General'),
            data.get('priority', 'Medium'),
            data.get('dueDate', None),
            data.get('status', 'Pending'),
            task_id
        ))
        conn.commit()
        return jsonify({"message": "Task updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Tasks WHERE TaskID = ?", (task_id,))
        conn.commit()
        return jsonify({"message": "Task deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

if __name__ == '__main__':
    app.run()

