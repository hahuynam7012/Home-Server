import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Hàm khởi tạo lại dữ liệu mẫu ban đầu cho bảng
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS StudentInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentName TEXT NOT NULL,
            Gender TEXT NOT NULL,
            StudentBirth TEXT NOT NULL,
            StudentHomeTown TEXT NOT NULL,
            StudentAcademicYear TEXT NOT NULL,
            StudentRoomNumber TEXT NOT NULL,
            PhoneNumber TEXT NOT NULL,
            CheckInDate TEXT NOT NULL
        )
    ''')
    
    # Kiểm tra nếu bảng trống thì thêm vài dòng dữ liệu mẫu
    cursor = conn.execute('SELECT COUNT(*) FROM StudentInfo')
    count = cursor.fetchone()[0]
    if count == 0:
        sample_data = [
            ('Nguyễn Văn An', 'Nam', '2004-05-12', 'Hà Nội', 'K22', 'P.101', '0912345678', '2024-09-01'),
            ('Trần Thị Bình', 'Nữ', '2005-08-20', 'Nam Định', 'K23', 'P.102', '0987654321', '2024-09-05'),
            ('Lê Hoàng Long', 'Nam', '2004-01-15', 'Thái Bình', 'K22', 'P.103', '0933445566', '2024-08-28')
        ]
        conn.executemany('''
            INSERT INTO StudentInfo (StudentName, Gender, StudentBirth, StudentHomeTown, StudentAcademicYear, StudentRoomNumber, PhoneNumber, CheckInDate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
        conn.commit()
    conn.close()

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    
    if search_query:
        # Tìm kiếm theo Tên, Phòng hoặc Quê quán
        query = '''
            SELECT * FROM StudentInfo 
            WHERE StudentName LIKE ? OR StudentRoomNumber LIKE ? OR StudentHomeTown LIKE ?
        '''
        like_pattern = f'%{search_query}%'
        data = conn.execute(query, (like_pattern, like_pattern, like_pattern)).fetchall()
    else:
        data = conn.execute('SELECT * FROM StudentInfo').fetchall()
        
    conn.close()
    return render_template('index.html', data=data, search_query=search_query)

@app.route('/reset-table', methods=['POST'])
def reset_table():
    conn = get_db_connection()
    # Xóa sạch bảng cũ và tạo lại dữ liệu mẫu mới
    conn.execute('DROP TABLE IF EXISTS StudentInfo')
    conn.commit()
    conn.close()
    
    init_db()  # Khởi tạo lại bảng và dữ liệu mẫu
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    # Chạy server lắng nghe trên toàn mạng nội bộ (truy cập qua IP máy)
    app.run(host='0.0.0.0', port=5000, debug=True)
