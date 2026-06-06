import os
import sqlite3
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import PyPDF2
import re
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('bills.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            renamed_filename TEXT NOT NULL,
            company_name TEXT,
            bill_number TEXT,
            vehicle_number TEXT,
            file_path TEXT NOT NULL,
            uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return ""

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return ""

def extract_bill_info(text, filename):
    """Extract company name, bill number, and vehicle number from text"""
    info = {
        'company_name': 'Unknown',
        'bill_number': 'Unknown',
        'vehicle_number': 'Unknown'
    }
    
    # Extract company name (common patterns)
    company_patterns = [
        r'(?:Company|Corp|Ltd|Inc|Company Name)[\s:]*([A-Za-z\s&]+)',
        r'^([A-Za-z\s&]{3,})(?:\n|$)'
    ]
    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            info['company_name'] = match.group(1).strip()
            break
    
    # Extract bill number
    bill_patterns = [
        r'(?:Invoice|Bill|Bill\s*No|Invoice\s*No)[\s:]*([A-Z0-9-]{3,})',
        r'(?:INV|BIL)[\s:]*([0-9]{3,})'
    ]
    for pattern in bill_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['bill_number'] = match.group(1).strip()
            break
    
    # Extract vehicle number
    vehicle_patterns = [
        r'(?:Vehicle|Car|Reg|Registration|Number Plate)[\s:]*([A-Z0-9]{2,})',
        r'(?:VIN|REG)[\s:]*([A-Z0-9]{6,})'
    ]
    for pattern in vehicle_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['vehicle_number'] = match.group(1).strip()
            break
    
    return info

def generate_filename(company, bill_no, vehicle_no, original_ext):
    """Generate new filename based on extracted information"""
    sanitized_company = re.sub(r'[^\w\s-]', '', company).replace(' ', '_')
    sanitized_bill = re.sub(r'[^\w-]', '', bill_no).replace(' ', '_')
    sanitized_vehicle = re.sub(r'[^\w-]', '', vehicle_no).replace(' ', '_')
    
    new_filename = f"{sanitized_company}_{sanitized_bill}_{sanitized_vehicle}.{original_ext}"
    return new_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        original_filename = filename
        file_ext = filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        saved_filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(file_path)
        
        # Extract text based on file type
        if file_ext == 'pdf':
            extracted_text = extract_text_from_pdf(file_path)
        else:
            extracted_text = extract_text_from_image(file_path)
        
        # Extract bill information
        bill_info = extract_bill_info(extracted_text, original_filename)
        
        # Generate new filename
        new_filename = generate_filename(
            bill_info['company_name'],
            bill_info['bill_number'],
            bill_info['vehicle_number'],
            file_ext
        )
        
        # Save to database
        conn = sqlite3.connect('bills.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO bills (original_filename, renamed_filename, company_name, bill_number, vehicle_number, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (original_filename, new_filename, bill_info['company_name'], bill_info['bill_number'], bill_info['vehicle_number'], file_path))
        bill_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': bill_id,
            'original_filename': original_filename,
            'renamed_filename': new_filename,
            'company_name': bill_info['company_name'],
            'bill_number': bill_info['bill_number'],
            'vehicle_number': bill_info['vehicle_number'],
            'extracted_text': extracted_text[:500]  # First 500 chars for preview
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills', methods=['GET'])
def get_bills():
    try:
        conn = sqlite3.connect('bills.db')
        c = conn.cursor()
        c.execute('SELECT id, original_filename, renamed_filename, company_name, bill_number, vehicle_number, uploaded_date FROM bills ORDER BY uploaded_date DESC')
        bills = c.fetchall()
        conn.close()
        
        bills_list = []
        for bill in bills:
            bills_list.append({
                'id': bill[0],
                'original_filename': bill[1],
                'renamed_filename': bill[2],
                'company_name': bill[3],
                'bill_number': bill[4],
                'vehicle_number': bill[5],
                'uploaded_date': bill[6]
            })
        
        return jsonify(bills_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    try:
        conn = sqlite3.connect('bills.db')
        c = conn.cursor()
        c.execute('SELECT * FROM bills WHERE id = ?', (bill_id,))
        bill = c.fetchone()
        conn.close()
        
        if not bill:
            return jsonify({'error': 'Bill not found'}), 404
        
        return jsonify({
            'id': bill[0],
            'original_filename': bill[1],
            'renamed_filename': bill[2],
            'company_name': bill[3],
            'bill_number': bill[4],
            'vehicle_number': bill[5],
            'file_path': bill[6],
            'uploaded_date': bill[7],
            'notes': bill[8]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills/<int:bill_id>', methods=['PUT'])
def update_bill(bill_id):
    try:
        data = request.json
        conn = sqlite3.connect('bills.db')
        c = conn.cursor()
        
        c.execute('''
            UPDATE bills
            SET company_name = ?, bill_number = ?, vehicle_number = ?, notes = ?
            WHERE id = ?
        ''', (data.get('company_name'), data.get('bill_number'), data.get('vehicle_number'), data.get('notes'), bill_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Bill updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    try:
        conn = sqlite3.connect('bills.db')
        c = conn.cursor()
        c.execute('SELECT file_path FROM bills WHERE id = ?', (bill_id,))
        result = c.fetchone()
        
        if result and os.path.exists(result[0]):
            os.remove(result[0])
        
        c.execute('DELETE FROM bills WHERE id = ?', (bill_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Bill deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_bills():
    try:
        query = request.args.get('q', '').lower()
        conn = sqlite3.connect('bills.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT id, original_filename, renamed_filename, company_name, bill_number, vehicle_number, uploaded_date
            FROM bills
            WHERE LOWER(company_name) LIKE ? OR LOWER(bill_number) LIKE ? OR LOWER(vehicle_number) LIKE ? OR LOWER(original_filename) LIKE ?
            ORDER BY uploaded_date DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        
        bills = c.fetchall()
        conn.close()
        
        bills_list = []
        for bill in bills:
            bills_list.append({
                'id': bill[0],
                'original_filename': bill[1],
                'renamed_filename': bill[2],
                'company_name': bill[3],
                'bill_number': bill[4],
                'vehicle_number': bill[5],
                'uploaded_date': bill[6]
            })
        
        return jsonify(bills_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
