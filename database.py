import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            seats TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("데이터베이스 초기화 완료!")

def get_booked_seats():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT seats FROM bookings')
    results = cursor.fetchall()
    
    booked_seats = []
    for row in results:
        seats = json.loads(row[0])
        booked_seats.extend(seats)
    
    conn.close()
    return booked_seats

def save_booking(booking_data):
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO bookings (booking_number, name, email, phone, seats)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            booking_data['booking_number'],
            booking_data['name'],
            booking_data['email'],
            booking_data['phone'],
            json.dumps(booking_data['seats'])
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"예매 저장 오류: {e}")
        conn.close()
        return False

def cancel_booking_by_info(name, email, phone):
    """정보 일치하는 예매 삭제"""
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    try:
        # 삭제하기 전에 예매 정보 가져오기
        cursor.execute('''
            SELECT booking_number, name, email, phone, seats 
            FROM bookings 
            WHERE name = ? AND email = ? AND phone = ?
        ''', (name, email, phone))
        
        booking_info = cursor.fetchone()
        
        if booking_info:
            # 예매 삭제
            cursor.execute('''
                DELETE FROM bookings 
                WHERE name = ? AND email = ? AND phone = ?
            ''', (name, email, phone))
            
            conn.commit()
            conn.close()
            
            # 삭제된 예매 정보 반환
            return {
                'booking_number': booking_info[0],
                'name': booking_info[1],
                'email': booking_info[2],
                'phone': booking_info[3],
                'seats': json.loads(booking_info[4])
            }
        else:
            conn.close()
            return None
            
    except Exception as e:
        print(f"예매 취소 오류: {e}")
        conn.close()
        return None    
    try:
        cursor.execute('''
            DELETE FROM bookings 
            WHERE name = ? AND email = ? AND phone = ?
        ''', (name, email, phone))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count > 0
    except Exception as e:
        print(f"예매 취소 오류: {e}")
        conn.close()
        return False

def cancel_all_bookings():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM bookings')
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"총 {deleted_count}개의 예매가 취소되었습니다.")
        return True
    except Exception as e:
        print(f"일괄 취소 오류: {e}")
        conn.close()
        return False
def get_booking_by_id(booking_id):
    """예매 ID로 예매 정보 가져오기"""
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT booking_number, name, email, phone, seats 
            FROM bookings 
            WHERE id = ?
        ''', (booking_id,))
        
        booking_info = cursor.fetchone()
        conn.close()
        
        if booking_info:
            return {
                'booking_number': booking_info[0],
                'name': booking_info[1],
                'email': booking_info[2],
                'phone': booking_info[3],
                'seats': json.loads(booking_info[4])
            }
        return None
    except Exception as e:
        print(f"예매 정보 조회 오류: {e}")
        conn.close()
        return None

def delete_booking_by_id(booking_id):
    """예매 ID로 예매 삭제"""
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count > 0
    except Exception as e:
        print(f"예매 삭제 오류: {e}")
        conn.close()
        return False
def get_booking_by_id(booking_id):
    """예매 ID로 예매 정보 가져오기"""
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT booking_number, name, email, phone, seats 
            FROM bookings 
            WHERE id = ?
        ''', (booking_id,))
        
        booking_info = cursor.fetchone()
        conn.close()
        
        if booking_info:
            return {
                'booking_number': booking_info[0],
                'name': booking_info[1],
                'email': booking_info[2],
                'phone': booking_info[3],
                'seats': json.loads(booking_info[4])
            }
        return None
    except Exception as e:
        print(f"예매 정보 조회 오류: {e}")
        conn.close()
        return None

def delete_booking_by_id(booking_id):
    """예매 ID로 예매 삭제"""
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count > 0
    except Exception as e:
        print(f"예매 삭제 오류: {e}")
        conn.close()
        return False
if __name__ == "__main__":
    init_db()