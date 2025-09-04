from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import random
import string
import requests
import os  # <- 이 줄 추가
from datetime import datetime
from database import init_db, get_booked_seats, save_booking, cancel_booking_by_info, cancel_all_bookings, get_booking_by_id, delete_booking_by_id

app = Flask(__name__)

# 이메일 설정
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
import os
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'jnjaeyun@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'focu hwst orep tdmz')
app.config['SECRET_KEY'] = 'gabor-booking-secret'

mail = Mail(app)

def generate_booking_number():
    return 'GB' + ''.join(random.choices(string.digits, k=6))

def send_confirmation_email(booking_data):
    msg = Message(
        '예매 확인 - 가보르 보디 기획 상영 및 토크',
        sender=app.config['MAIL_USERNAME'],
        recipients=[booking_data['email']]
    )
    
    msg.html = f'''
    <h2>예매 확인서</h2>
    <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
        <h3>&lt;가보르 보디 기획 상영 및 토크&gt;</h3>
        <p><strong>예매번호:</strong> {booking_data['booking_number']}</p>
        <p><strong>이름:</strong> {booking_data['name']}</p>
        <p><strong>좌석:</strong> {', '.join(booking_data['seats'])}</p>
        <p><strong>일시:</strong> 2025년 9월 15일 (월) 17:00 ~ 21:00</p>
        <hr>
        <p>입장 시 본 이메일을 제시해주세요.</p>
    </div>
    '''
    
    mail.send(msg)
def send_cancellation_email(booking_data):
    """예매 취소 확인 이메일 발송"""
    msg = Message(
        '예매 취소 확인 - 가보르 보디 기획 상영 및 토크',
        sender=app.config['MAIL_USERNAME'],
        recipients=[booking_data['email']]
    )
    
    msg.html = f'''
    <h2>예매 취소 확인</h2>
    <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; font-family: Arial;">
        <h3>&lt;가보르 보디 기획 상영 및 토크&gt;</h3>
        <p><strong>예매번호:</strong> {booking_data['booking_number']}</p>
        <p><strong>이름:</strong> {booking_data['name']}</p>
        <p><strong>좌석:</strong> {', '.join(booking_data['seats'])}</p>
        <p><strong>일시:</strong> 2025년 9월 15일 (월) 17:00 ~ 21:00</p>
        <hr>
        <p style="color: #e74c3c; font-weight: bold;">예매가 취소되었습니다.</p>
        <p style="color: #666;">궁금한 사항이 있으시면 문의해주세요.</p>
    </div>
    '''
    
    mail.send(msg)
@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '')
    if any(mobile in user_agent for mobile in ['Mobile', 'Android', 'iPhone', 'iPad']):
        return render_template('mobile.html')
    else:
        return render_template('index.html')
@app.route('/cancel')
def cancel_page():
    return render_template('cancel.html')

@app.route('/admin')
def admin_page():
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    password = data.get('password')
    
    if password == '0915':
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '비밀번호가 틀렸습니다.'})

@app.route('/api/booked-seats')
def api_booked_seats():
    booked_seats = get_booked_seats()
    return jsonify(booked_seats)

@app.route('/api/admin/bookings')
def get_all_bookings():
    import sqlite3
    import json
    
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
    results = cursor.fetchall()
    
    bookings = []
    for row in results:
        bookings.append({
            'id': row[0],
            'booking_number': row[1],
            'name': row[2],
            'email': row[3],
            'phone': row[4],
            'seats': json.loads(row[5]),
            'created_at': row[6]
        })
    
    conn.close()
    return jsonify(bookings)

@app.route('/api/admin/cancel-all', methods=['POST'])
def api_cancel_all_bookings():
    try:
        if cancel_all_bookings():
            return jsonify({
                'success': True,
                'message': '모든 예매가 취소되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '취소 처리 중 오류가 발생했습니다.'
            }), 500
    except Exception as e:
        print(f"일괄 취소 오류: {e}")
        return jsonify({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }), 500
@app.route('/api/admin/cancel-booking/<booking_id>', methods=['POST'])
def admin_cancel_booking(booking_id):
    try:
        booking_info = get_booking_by_id(booking_id)
        
        if booking_info and delete_booking_by_id(booking_id):
            # 취소 확인 이메일 발송
            try:
                send_cancellation_email(booking_info)
                print(f"관리자 취소 메일 발송 완료: {booking_info['email']}")
            except Exception as e:
                print(f"취소 메일 발송 오류: {e}")
            
            return jsonify({
                'success': True,
                'message': '예매가 취소되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '예매 정보를 찾을 수 없습니다.'
            }), 404
    except Exception as e:
        print(f"관리자 예매 취소 오류: {e}")
        return jsonify({
            'success': False,
            'message': '취소 처리 중 오류가 발생했습니다.'
        }), 500
@app.route('/api/cancel-booking', methods=['POST'])
def api_cancel_booking():
    try:
        data = request.json
        name = data['name']
        email = data['email']
        phone = data['phone']
        
        cancelled_booking = cancel_booking_by_info(name, email, phone)
        
        if cancelled_booking:
            # 취소 확인 이메일 발송
            try:
                send_cancellation_email(cancelled_booking)
                print(f"예매 취소 메일 발송 완료: {email}")
            except Exception as e:
                print(f"취소 메일 발송 오류: {e}")
            return jsonify({
                'success': True,
                'message': '예매가 취소되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '일치하는 예매 정보를 찾을 수 없습니다.'
            }), 404
    except Exception as e:
        print(f"예매 취소 오류: {e}")
        return jsonify({
            'success': False,
            'message': '취소 처리 중 오류가 발생했습니다.'
        }), 500

@app.route('/api/booking', methods=['POST'])
def api_booking():
    try:
        data = request.json
        booking_number = generate_booking_number()
        
        booking_data = {
            'booking_number': booking_number,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'seats': data['seats']
        }
        
        if save_booking(booking_data):
            return jsonify({
                'success': True,
                'booking_number': booking_number,
                'message': '예매가 완료되었습니다!'
            })
        else:
            return jsonify({
                'success': False,
                'message': '예매 처리 중 오류가 발생했습니다.'
            }), 500
            
    except Exception as e:
        print(f"예매 처리 오류: {e}")
        return jsonify({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }), 500
@app.route('/api/admin/download-excel')
def download_excel():
    import sqlite3
    import json
    from datetime import datetime
    import io
    from flask import send_file
    
    try:
        # 모든 예매 정보 가져오기
        conn = sqlite3.connect('bookings.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        
        # CSV 형태로 데이터 준비 (엑셀 대신 CSV 사용)
        csv_data = "예매번호,이름,이메일,연락처,좌석,예매일시\n"
        
        for row in results:
            booking_number = row[1]
            name = row[2]
            email = row[3]
            phone = row[4]
            seats = ', '.join(json.loads(row[5]))
            created_at = row[6]
            
            csv_data += f'"{booking_number}","{name}","{email}","{phone}","{seats}","{created_at}"\n'
        
        # 메모리에 CSV 파일 생성
        output = io.StringIO()
        output.write(csv_data)
        output.seek(0)
        
        # 바이트로 변환
        byte_output = io.BytesIO()
        byte_output.write(output.getvalue().encode('utf-8-sig'))  # BOM 추가로 한글 깨짐 방지
        byte_output.seek(0)
        
        return send_file(
            byte_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'gabor_bookings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        print(f"엑셀 다운로드 오류: {e}")
        return jsonify({
            'success': False,
            'message': '다운로드 처리 중 오류가 발생했습니다.'
        }), 500
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print("🎬 가보르 보디 예매 시스템이 시작됩니다!")
    app.run(debug=False, host='0.0.0.0', port=port)
else:
    # Vercel 배포용
    init_db()
















