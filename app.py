from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'field_instrumentation_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///field_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---

class PipeCalculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    material = db.Column(db.String(50))
    external_diameter = db.Column(db.Float)
    wall_thickness = db.Column(db.Float)
    internal_diameter = db.Column(db.Float)
    area_m2 = db.Column(db.Float)

class CalibrationSession(db.Model):
    id = db.Column(db.String(50), primary_key=True) # The "Room Code"
    start_time = db.Column(db.Float, nullable=True) # Timestamp when the test started
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    interval_seconds = db.Column(db.Integer, default=60)

class CalibrationReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), db.ForeignKey('calibration_session.id'))
    user_identifier = db.Column(db.String(50)) # 'A' or 'B' (or username)
    minute_index = db.Column(db.Integer) # 1 to 10
    value = db.Column(db.Float)
# --- EQUIPMENT KNOWLEDGE BASE ---

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    type = db.Column(db.String(50)) # 'Eletromagnético', 'Ultrassônico'
    power_supply = db.Column(db.String(50))
    password_user = db.Column(db.String(50))
    password_admin = db.Column(db.String(50))
    menu_shortcuts = db.Column(db.Text)
    notes = db.Column(db.Text)

@app.route('/biblioteca_equipamentos')
def biblioteca_equipamentos():
    # Only return all equipments, search is client-side
    equipments = Equipment.query.all()
    return render_template('biblioteca_equipamentos.html', equipments=equipments)

@app.route('/api/add_equipment', methods=['POST'])
def add_equipment():
    data = request.form
    new_eq = Equipment(
        brand=data.get('brand'),
        model=data.get('model'),
        type=data.get('type'),
        power_supply=data.get('power_supply'),
        password_user=data.get('password_user'),
        password_admin=data.get('password_admin'),
        menu_shortcuts=data.get('menu_shortcuts'),
        notes=data.get('notes')
    )
    db.session.add(new_eq)
    db.session.commit()
    return redirect(url_for('biblioteca_equipamentos'))

def seed_equipment_data():
    if Equipment.query.first():
        return # Already seeded

    initial_data = [
        {
            'brand': 'Siemens', 'model': 'MAG 5000', 'type': 'Eletromagnético', 'power_supply': '220V AC',
            'password_user': 'N/A', 'password_admin': 'N/A', 
            'menu_shortcuts': '', 'notes': 'Senha não informada.'
        },
        {
            'brand': 'Gaiatec', 'model': 'Não Informado', 'type': 'Ultrassônico', 'power_supply': '12-36V DC',
            'password_user': 'Não tem', 'password_admin': '', 
            'menu_shortcuts': '', 'notes': 'Fator K: Menu 45. Nº Série: Menu 61. OBS: Serial só no secundário.'
        },
        {
            'brand': 'Sonesolute', 'model': 'Ecomag', 'type': 'Eletromagnético', 'power_supply': '12-36V DC',
            'password_user': '1050000...', 'password_admin': '', 
            'menu_shortcuts': 'Menu: Reservado', 'notes': 'Carritel com Nº Serial nos dois.'
        },
        {
            'brand': 'Sitelab', 'model': 'SL 1168', 'type': 'Ultrassônico', 'power_supply': '12-36V DC',
            'password_user': 'Não tem', 'password_admin': '', 
            'menu_shortcuts': '', 'notes': 'Fator K: Menu 45. Nº Série: Menu 61. OBS: Serial só no secundário.'
        },
        {
            'brand': 'Contech', 'model': 'CTHHD "6"', 'type': 'Eletromagnético', 'power_supply': '220V AC',
            'password_user': '03210', 'password_admin': '19818', 
            'menu_shortcuts': 'Aperta e solta o primeiro e último botão para desbloquear/entrar senha. Segura o último para sair.', 
            'notes': 'Menu Sensor Factor mostra o Fator K. Carritel com Nº Serial nos dois.'
        },
        {
            'brand': 'Flowmeter', 'model': 'Genérico', 'type': 'Ultrassônico', 'power_supply': '12-36V DC',
            'password_user': '0525000...', 'password_admin': '', 
            'menu_shortcuts': '', 'notes': 'Carritel com Nº Serial nos dois.'
        },
        {
            'brand': 'Euromag', 'model': 'Carretel', 'type': 'Eletromagnético', 'power_supply': 'N/A',
            'password_user': '', 'password_admin': '', 
            'menu_shortcuts': '', 'notes': 'Senha: 231042'
        }
    ]

    for item in initial_data:
        record = Equipment(**item)
        db.session.add(record)
    
    db.session.commit()

# Initialize DB
with app.app_context():
    db.create_all()
    seed_equipment_data()

# Data transcribed from user request
PIPE_STANDARDS = [
    {'dn_pol': '2"',     'dn_mm': 50,  'flange': None, 'k7': None, 'k9': None,  'cimento': None, 'fofo': None, 'pba12': 2.7, 'pba15': 3.3, 'pba20': 4.3},
    {'dn_pol': '2 1/4"', 'dn_mm': 60,  'flange': None, 'k7': None, 'k9': None,  'cimento': None, 'fofo': None, 'pba12': 3.4, 'pba15': 4.2, 'pba20': 5.3},
    {'dn_pol': '2 1/2"', 'dn_mm': 75,  'flange': None, 'k7': None, 'k9': None,  'cimento': None, 'fofo': None, 'pba12': 3.9, 'pba15': 4.7, 'pba20': 6.1},
    {'dn_pol': '3"',     'dn_mm': 80,  'flange': 6.0,  'k7': None, 'k9': 6.0,   'cimento': 2.5,  'fofo': None, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '4"',     'dn_mm': 100, 'flange': 6.0,  'k7': None, 'k9': 6.0,   'cimento': 2.5,  'fofo': 4.8,  'pba12': 5.0, 'pba15': 6.1, 'pba20': 7.8},
    {'dn_pol': '6"',     'dn_mm': 150, 'flange': 6.0,  'k7': 5.2,  'k9': 6.0,   'cimento': 2.5,  'fofo': 6.8,  'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '8"',     'dn_mm': 200, 'flange': 6.3,  'k7': 5.4,  'k9': 6.3,   'cimento': 2.5,  'fofo': 8.9,  'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '10"',    'dn_mm': 250, 'flange': 6.8,  'k7': 5.5,  'k9': 6.8,   'cimento': 2.5,  'fofo': 11.0, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '12"',    'dn_mm': 300, 'flange': 7.2,  'k7': 5.7,  'k9': 7.2,   'cimento': 2.5,  'fofo': 13.1, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '14"',    'dn_mm': 350, 'flange': 7.7,  'k7': 5.9,  'k9': 7.7,   'cimento': 4.5,  'fofo': 15.2, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '16"',    'dn_mm': 400, 'flange': 8.1,  'k7': 6.3,  'k9': 8.1,   'cimento': 4.5,  'fofo': 17.2, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '18"',    'dn_mm': 450, 'flange': 8.6,  'k7': 6.7,  'k9': 8.6,   'cimento': 4.5,  'fofo': None, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '20"',    'dn_mm': 500, 'flange': 9.0,  'k7': 7.0,  'k9': 9.0,   'cimento': 4.5,  'fofo': 21.3, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '24"',    'dn_mm': 600, 'flange': 9.9,  'k7': 7.7,  'k9': 9.9,   'cimento': 4.5,  'fofo': None, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '28"',    'dn_mm': 700, 'flange': 14.4, 'k7': 8.4,  'k9': 10.8,  'cimento': 5.5,  'fofo': None, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '32"',    'dn_mm': 800, 'flange': 15.6, 'k7': 9.1,  'k9': 11.7,  'cimento': 5.5,  'fofo': None, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '36"',    'dn_mm': 900, 'flange': 16.8, 'k7': 9.8,  'k9': 12.6,  'cimento': 5.5,  'fofo': None, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '40"',    'dn_mm': 1000,'flange': 18.0, 'k7': 10.5, 'k9': 13.5,  'cimento': 5.5,  'fofo': None, 'pba12': None, 'pba15': None, 'pba20': None},
    {'dn_pol': '48"',    'dn_mm': 1200,'flange': 20.4, 'k7': 11.9, 'k9': 15.3,  'cimento': 5.5,  'fofo': None, 'pba12': None, 'pba15': None, 'pba20': None},
]

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tubulacao', methods=['GET', 'POST'])
def tubulacao():
    result = None
    closest_pipe = None
    
    if request.method == 'POST':
        try:
            # Inputs
            input_method = request.form.get('input_method') # 'diameter' or 'circumference'
            input_val = float(request.form.get('input_val'))
            material_key = request.form.get('material_key') # 'k7', 'k9', 'pba12', etc.
            has_cement = request.form.get('has_cement') == 'on'
            
            # 1. Calc Diameter
            measured_diam = input_val
            if input_method == 'circumference':
                measured_diam = input_val / math.pi
            
            # 2. Find closest DN in table
            # Logic: Find row with min absolute difference between DN_mm and measured_diam
            # Note: The table DN is Nominal. Real Measure might be slightly different. 
            # We assume user wants the standard values for the CLOSEST nominal size.
            
            closest_dist = float('inf')
            
            for row in PIPE_STANDARDS:
                dist = abs(row['dn_mm'] - measured_diam)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_pipe = row
            
            # 3. Get Thickness
            wall_thickness = 0
            if closest_pipe and closest_pipe.get(material_key) is not None:
                wall_thickness = closest_pipe[material_key]
            
            # 4. Check Cement
            cement_thickness = 0
            if has_cement:
                # Use table value if present, else Use rule of thumb
                if closest_pipe.get('cimento'):
                    cement_thickness = closest_pipe['cimento']
                else:
                    # Fallback logic from prompt
                    if closest_pipe['dn_mm'] < 350:
                        cement_thickness = 2.5
                    else:
                        cement_thickness = 4.5
            
            # 5. Final Calc
            # ID = External_Diameter - 2*Wall - 2*Cement
            # Wait, usually the measurement IS the external diameter.
            # If user inputs Circumference/Diameter, that is the OD.
            # BUT the table is based on DN. 
            # The Prompt says: "Parametrização no medidor... Informar: Material, Diametro, Espessura, Espessura Revestimento".
            # The Application should OUTPUT these values for the user to type in the meter.
            
            # So we supply:
            # - The Measured Diameter (Ext)
            # - The Looked-up Wall Thickness
            # - The Looked-up Cement Thickness
            # - (Optional) Calculated Internal Diameter
            
            total_wall = wall_thickness # Cement is usually a separate parameter in meters, but here we calculate ID.
            
            int_diam = measured_diam - (2 * wall_thickness) - (2 * cement_thickness)
            
            # Area
            radius_m = (int_diam / 2) / 1000.0
            area = math.pi * (radius_m ** 2) if int_diam > 0 else 0
            
            result = {
                'measured_diam': round(measured_diam, 2),
                'matched_dn_mm': closest_pipe['dn_mm'],
                'matched_dn_pol': closest_pipe['dn_pol'],
                'material_key': material_key,
                'wall_thickness': wall_thickness,
                'cement_thickness': cement_thickness,
                'int_diam': round(int_diam, 2),
                'area': round(area, 6)
            }
            
            # Only save validcalcs
            if wall_thickness > 0:
                calc = PipeCalculation(
                    material=material_key,
                    external_diameter=measured_diam,
                    wall_thickness=wall_thickness,
                    internal_diameter=int_diam,
                    area_m2=area
                )
                db.session.add(calc)
                db.session.commit()
            else:
                result['width_warning'] = True
                
        except (ValueError, TypeError):
             result = {'error': 'Valor inválido'}

    return render_template('tubulacao.html', result=result, pipes=PIPE_STANDARDS)

@app.route('/afericao')
def afericao():
    return render_template('afericao.html')

@app.route('/afericao/<session_id>')
def afericao_session(session_id):
    return render_template('afericao_session.html', session_id=session_id)

# --- API FOR SYNC ---

@app.route('/api/create_session', methods=['POST'])
def create_session():
    import random, string
    data = request.json or {} 
    interval = int(data.get('interval', 60))
    
    # Generate short random code
    session_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    new_session = CalibrationSession(id=session_id, interval_seconds=interval)
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'session_id': session_id})

@app.route('/api/start_test', methods=['POST'])
def start_test():
    data = request.json
    session_id = data.get('session_id')
    session = CalibrationSession.query.get(session_id)
    if session:
        import time
        # Set start time to 5 seconds in the fluid future (synchronization buffer)
        session.start_time = time.time() + 5 
        db.session.commit()
        return jsonify({'status': 'started', 'start_time': session.start_time})
    return jsonify({'error': 'Session not found'}), 404

@app.route('/api/session_status/<session_id>')
def session_status(session_id):
    session = CalibrationSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Not found'}), 404
    
    # Get count of readings
    readings = CalibrationReading.query.filter_by(session_id=session_id).all()
    count_a = len([r for r in readings if r.user_identifier == 'A'])
    count_b = len([r for r in readings if r.user_identifier == 'B'])
    
    return jsonify({
        'start_time': session.start_time,
        'interval': session.interval_seconds,
        'count_a': count_a,
        'count_b': count_b
    })

@app.route('/api/submit_reading', methods=['POST'])
def submit_reading():
    data = request.json
    try:
        reading = CalibrationReading(
            session_id=data['session_id'],
            user_identifier=data['user'],
            minute_index=data['minute'],
            value=float(data['value'])
        )
        db.session.add(reading)
        db.session.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/get_results/<session_id>')
def get_results(session_id):
    readings = CalibrationReading.query.filter_by(session_id=session_id).all()
    
    data_a = {r.minute_index: r.value for r in readings if r.user_identifier == 'A'}
    data_b = {r.minute_index: r.value for r in readings if r.user_identifier == 'B'}
    
    # Calculate stats if we have data
    avg_a = sum(data_a.values()) / len(data_a) if data_a else 0
    avg_b = sum(data_b.values()) / len(data_b) if data_b else 0
    
    error_pct = 0
    if avg_a > 0 and avg_b > 0:
        # User requested formula: (Maior / Menor - 1) * 100
        val_max = max(avg_a, avg_b)
        val_min = min(avg_a, avg_b)
        error_pct = (val_max / val_min - 1) * 100
    
    status = 'APROVADO' if error_pct <= 2 else 'REPROVADO'
    
    return jsonify({
        'data_a': data_a,
        'data_b': data_b,
        'avg_a': round(avg_a, 2),
        'avg_b': round(avg_b, 2),
        'error_pct': round(error_pct, 2),
        'status': status
    })

# --- LOW FLOW CUTOFF MODULE ---

@app.route('/corte_vazao')
def corte_vazao():
    # Options for DN with Inch equivalents
    dn_options = [
        {'mm': 15, 'inch': '1/2"'},
        {'mm': 20, 'inch': '3/4"'},
        {'mm': 25, 'inch': '1"'},
        {'mm': 32, 'inch': '1 1/4"'},
        {'mm': 40, 'inch': '1 1/2"'},
        {'mm': 50, 'inch': '2"'},
        {'mm': 65, 'inch': '2 1/2"'},
        {'mm': 80, 'inch': '3"'},
        {'mm': 100, 'inch': '4"'},
        {'mm': 125, 'inch': '5"'},
        {'mm': 150, 'inch': '6"'},
        {'mm': 200, 'inch': '8"'},
        {'mm': 250, 'inch': '10"'},
        {'mm': 300, 'inch': '12"'},
        {'mm': 350, 'inch': '14"'},
        {'mm': 400, 'inch': '16"'},
        {'mm': 450, 'inch': '18"'},
        {'mm': 500, 'inch': '20"'},
        {'mm': 600, 'inch': '24"'},
        {'mm': 700, 'inch': '28"'},
        {'mm': 800, 'inch': '32"'},
        {'mm': 900, 'inch': '36"'},
        {'mm': 1000, 'inch': '40"'},
        {'mm': 1200, 'inch': '48"'}
    ]
    return render_template('corte_vazao.html', dn_options=dn_options)

@app.route('/calculate_cutoff', methods=['POST'])
def calculate_cutoff():
    try:
        dn_mm = int(request.form.get('dn', 0))
        velocity = float(request.form.get('velocity', 0.1))
        model = request.form.get('model', 'generic')
        
        # Formula: Flow = (pi * (dn_m)^2 / 4) * v * 3600
        # dn_m = dn_mm / 1000
        flow_m3h = (math.pi * ((dn_mm / 1000.0) ** 2) / 4) * velocity * 3600
        
        flow_formatted = f"{flow_m3h:.3f}"
        
        # Tip Logic
        tips = {
            'contech': "Menu: Setup > Alarm > Low Flow Cutoff (ou L-Cut). Senha padrão: 19818 ou 00521.",
            'sitelab': "Menu: M51 (Low Flow Cutoff Value). Digite o valor calculado.",
            'ecomag': "Menu: Parameter Set > Cut Off. Senha padrão: 0000.",
            'siemens': "Menu: Parameters > Low Flow Cutoff. Unidade deve estar em m³/h.",
            'generic': "Procure por: 'Low Flow Cutoff', 'Zero Cut' ou 'Band' no manual."
        }
        
        tip_text = tips.get(model, tips['generic'])
        
        # Return HTML fragment for HTMX
        return f"""
        <div class="card card-field bg-white border-primary mb-3 animate-fade-in">
            <div class="card-body text-center">
                <h5 class="text-muted mb-2">Ajuste o corte para:</h5>
                <h1 class="display-4 fw-bold text-primary mb-0">{flow_formatted} <small class="fs-4 text-muted">m³/h</small></h1>
                
                <div class="mt-3 pt-3 border-top d-inline-block">
                    <span class="badge bg-light text-secondary border">Velocidade: {velocity} m/s</span>
                </div>
            </div>
        </div>
        
        <div class="alert alert-info d-flex align-items-start" role="alert">
            <i class="fas fa-lightbulb mt-1 me-3 fa-lg"></i>
            <div>
                <strong>Dica de Acesso:</strong><br>
                {tip_text}
            </div>
        </div>
        """
        
    except Exception as e:
        return f"<div class='alert alert-danger'>Erro no cálculo: {str(e)}</div>"

# --- K-FACTOR CALCULATOR MODULE ---

@app.route('/sensor_pressao')
def sensor_pressao():
    return render_template('sensor_pressao.html')

@app.route('/calculadora_k')
def calculadora_k():
    return render_template('calculadora_k.html')

@app.route('/calculate_k', methods=['POST'])
def calculate_k():
    try:
        current_k = float(request.form.get('current_k', 1.0))
        meter_val = float(request.form.get('meter_val', 0))
        ref_val = float(request.form.get('ref_val', 0))
        
        if meter_val == 0:
            return "" # Don't divide by zero, just wait for input
            
        # Logic: Ratio = Ref / Meter
        ratio = ref_val / meter_val
        new_k = current_k * ratio
        
        # Error %: ((Meter - Ref) / Ref) * 100 ... Wait, usually error is (Measured - True) / True
        # Prompt says: "((Meter_Reading - Reference_Value) / Reference_Value) * 100"
        if ref_val != 0:
            error_pct = ((meter_val - ref_val) / ref_val) * 100
        else:
            error_pct = 0
            
        new_k_formatted = f"{new_k:.5f}"
        error_formatted = f"{error_pct:.2f}"
        
        err_color = "text-danger" if abs(error_pct) > 2 else "text-success"
        
        return f"""
        <div class="card card-field bg-white border-primary mb-3 animate-fade-in">
            <div class="card-body text-center">
                <h5 class="text-muted mb-2">Novo Fator K</h5>
                <h1 class="display-3 fw-bold text-primary mb-0">{new_k_formatted}</h1>
                <p class="text-muted small mt-2">Insira este valor no menu 'Sensor Factor' ou 'GK'</p>
                
                <div class="mt-3 pt-3 border-top">
                    <span class="{err_color} fw-bold">
                        <i class="fas fa-exclamation-triangle me-1"></i>
                        Erro Encontrado: {error_formatted}%
                    </span>
                    <br>
                    <small class="text-muted">O medidor estava lendo {abs(error_pct):.2f}% {"a mais" if error_pct > 0 else "a menos"} que a referência.</small>
                </div>
            </div>
        </div>
        """
        
    except ValueError:
        return "" # Handle empty inputs gracefully during typing
    except Exception as e:
        return f"<div class='alert alert-danger'>Erro: {str(e)}</div>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
