from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
from models import init_db, Reading
import pandas as pd, io, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'suncraftdogana2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

Session = init_db()
session = Session()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/save', methods=['POST'])
def save():
    data = request.json
    reading = Reading(
        operator=data.get('operator',''),
        plant='IT DOGANA ELECNOR',
        ncu=data.get('ncu',''),
        tcu_mac=data.get('ocr_text',''),
        latitude=data.get('lat'),
        longitude=data.get('lon')
    )
    session.add(reading)
    session.commit()
    socketio.emit('new', {'id': reading.id, 'operator': reading.operator, 'ncu': reading.ncu, 'tcu_mac': reading.tcu_mac})
    return jsonify({'status':'ok'})

@app.route('/api/delete_last', methods=['POST'])
def delete_last():
    last = session.query(Reading).order_by(Reading.id.desc()).first()
    if last:
        session.delete(last)
        session.commit()
        socketio.emit('deleted', {'id': last.id})
        return jsonify({'status':'deleted'})
    return jsonify({'status':'empty'})

@app.route('/download_excel')
def download_excel():
    data = session.query(Reading).order_by(Reading.ncu, Reading.id).all()
    df = pd.DataFrame([{
        'NCU': r.ncu, 'MAC': r.tcu_mac, 'Latitud': r.latitude, 'Longitud': r.longitude,
        'Operario': r.operator, 'Fecha': r.timestamp.strftime('%Y-%m-%d'), 'Hora': r.timestamp.strftime('%H:%M:%S')
    } for r in data])
    if df.empty:
        df = pd.DataFrame(columns=['NCU','MAC','Latitud','Longitud','Operario','Fecha','Hora'])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='TCU')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='tcu_suncraft.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
