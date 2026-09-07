import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'khoa_bi_mat_cho_session_nay'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'Database', 'Home_Server.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS StudentInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            StudentName TEXT NOT NULL,
            Gender TEXT NOT NULL,
            StudentBirth TEXT NOT NULL,
            StudentHomeTown TEXT NOT NULL,
            StudentAcademicYear TEXT NOT NULL,
            StudentRoomNumber TEXT NOT NULL,
            PhoneNumber TEXT NOT NULL,
            CheckInDate TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grid')
def grid():
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    
    if search_query:
        query = '''
            SELECT * FROM StudentInfo 
            WHERE StudentName LIKE ? OR StudentRoomNumber LIKE ? OR StudentHomeTown LIKE ?
        '''
        like_pattern = f'%{search_query}%'
        data = conn.execute(query, (like_pattern, like_pattern, like_pattern)).fetchall()
    else:
        data = conn.execute('SELECT * FROM StudentInfo').fetchall()
        
    conn.close()
    return render_template('table.html', data=data, search_query=search_query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    current_user = session['username']
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['StudentName']
        gender = request.form['Gender']
        birth = request.form['StudentBirth']
        hometown = request.form['StudentHomeTown']
        academic_year = request.form['StudentAcademicYear']
        room = request.form['StudentRoomNumber']
        phone = request.form['PhoneNumber']
        checkin = request.form['CheckInDate']
        
        existing = conn.execute('SELECT * FROM StudentInfo WHERE username = ?', (current_user,)).fetchone()
        
        if existing:
            conn.execute('''
                UPDATE StudentInfo 
                SET StudentName = ?, Gender = ?, StudentBirth = ?, StudentHomeTown = ?, 
                    StudentAcademicYear = ?, StudentRoomNumber = ?, PhoneNumber = ?, CheckInDate = ?
                WHERE username = ?
            ''', (name, gender, birth, hometown, academic_year, room, phone, checkin, current_user))
        else:
            conn.execute('''
                INSERT INTO StudentInfo (username, StudentName, Gender, StudentBirth, StudentHomeTown, StudentAcademicYear, StudentRoomNumber, PhoneNumber, CheckInDate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (current_user, name, gender, birth, hometown, academic_year, room, phone, checkin))
            
        conn.commit()
        conn.close()
        return redirect(url_for('grid'))
        
    student_data = conn.execute('SELECT * FROM StudentInfo WHERE username = ?', (current_user,)).fetchone()
    conn.close()
    
    return render_template('profile.html', student=student_data)

@app.route('/reset-table', methods=['POST'])
def reset_table():
    conn = get_db_connection()
    conn.execute('DROP TABLE IF EXISTS StudentInfo')
    conn.execute('DROP TABLE IF EXISTS Users')
    conn.commit()
    conn.close()
    
    init_db()
    return redirect(url_for('grid'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
