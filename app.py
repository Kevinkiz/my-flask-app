from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import sqlite3
import os
import csv
from io import StringIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect('tax_records.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tax_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "FirmName" TEXT,
            "Date_Period" TEXT,
            "net_profit" REAL,
            "net_profit2" REAL,
            "Depreciation" REAL,
            "Bribes" REAL,
            "Penalties" REAL,
            "Gifts & Offers" REAL,
            "Donations" REAL,
            "Others" REAL,
            "Total Non Allowable Deductions" REAL,
            "Adjusted Net Profit Before Tax" REAL,
            "Total Wear & Tear2" REAL,
            "25% Start up Costs" REAL,
            "5% Industrial Building Deduction" REAL,
            "20% Initial Building Allowance" REAL,
            "Horticultural Exp" REAL,
            "Others NAD" REAL,
            "Total Allowable Deductions" REAL,
            "Chargeable Income" REAL,
            "Loss B/f" REAL,
            "Adjusted Chargeable Income" REAL,
            "30% Cooperation Tax" REAL,
            "WHTPaid" REAL,
            "TaxCredit" REAL,
            "ProvisionalTaxPaid" REAL,
            "TaxPayableRecoverable" REAL,
            "Computers,Data & Software" REAL,
            "Plant & Machinery(Farming,Mining,Manufacture)" REAL,
            "Automobiles<=60Million" REAL,
            "Others not in any Class" REAL,
            "file" TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper to safely convert to float
def to_float(form, field):
    try:
        return float(form.get(field, 0) or 0)
    except ValueError:
        return 0

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compute', methods=['POST'])
def compute():
    form = request.form
    file = request.files.get('file')
    filename = None
    if file and file.filename != '':
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = sqlite3.connect('tax_records.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO tax_records (
            "FirmName", "Date_Period", "net_profit", "net_profit2", "Depreciation",
            "Bribes", "Penalties", "Gifts & Offers", "Donations", "Others",
            "Total Non Allowable Deductions", "Adjusted Net Profit Before Tax",
            "Total Wear & Tear2", "25% Start up Costs", "5% Industrial Building Deduction",
            "20% Initial Building Allowance", "Horticultural Exp", "Others NAD",
            "Total Allowable Deductions", "Chargeable Income", "Loss B/f",
            "Adjusted Chargeable Income", "30% Cooperation Tax", "WHTPaid",
            "TaxCredit", "ProvisionalTaxPaid", "TaxPayableRecoverable",
            "Computers,Data & Software",
            "Plant & Machinery(Farming,Mining,Manufacture)",
            "Automobiles<=60Million",
            "Others not in any Class",
            "file"
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        form.get('FirmName'),
        form.get('Date_Period'),
        to_float(form, 'net_profit'),
        to_float(form, 'net_profit2'),
        to_float(form, 'Depreciation'),
        to_float(form, 'Bribes'),
        to_float(form, 'Penalties'),
        to_float(form, 'Gifts & Offers'),
        to_float(form, 'Donations'),
        to_float(form, 'Others'),
        to_float(form, 'Total Non Allowable Deductions'),
        to_float(form, 'Adjusted Net Profit Before Tax'),
        to_float(form, 'Total Wear & Tear2'),
        to_float(form, '25% Start up Costs'),
        to_float(form, '5% Industrial Building Deduction'),
        to_float(form, '20% Initial Building Allowance'),
        to_float(form, 'Horticultural Exp'),
        to_float(form, 'Others NAD'),
        to_float(form, 'Total Allowable Deductions'),
        to_float(form, 'Chargeable Income'),
        to_float(form, 'Loss B/f'),
        to_float(form, 'Adjusted Chargeable Income'),
        to_float(form, '30% Cooperation Tax'),
        to_float(form, 'WHTPaid'),
        to_float(form, 'TaxCredit'),
        to_float(form, 'ProvisionalTaxPaid'),
        to_float(form, 'TaxPayableRecoverable'),
        to_float(form, 'Computers,Data & Software'),
        to_float(form, 'Plant & Machinery(Farming,Mining,Manufacture)'),
        to_float(form, 'Automobiles<=60Million'),
        to_float(form, 'Others not in any Class'),
        filename
    ))
    conn.commit()
    conn.close()

    return '''
        <h1>Record saved successfully!</h1>
        <a href="/records">View All Records</a><br>
        <a href="/">Back to Form</a>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/records')
def view_records():
    conn = sqlite3.connect('tax_records.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tax_records')
    rows = c.fetchall()
    conn.close()

    columns = [
        "FirmName", "Date_Period", "net_profit", "net_profit2", "Depreciation",
        "Bribes", "Penalties", "Gifts & Offers", "Donations", "Others",
        "Total Non Allowable Deductions", "Adjusted Net Profit Before Tax",
        "Total Wear & Tear2", "25% Start up Costs", "5% Industrial Building Deduction",
        "20% Initial Building Allowance", "Horticultural Exp", "Others NAD",
        "Total Allowable Deductions", "Chargeable Income", "Loss B/f",
        "Adjusted Chargeable Income", "30% Cooperation Tax", "WHTPaid",
        "TaxCredit", "ProvisionalTaxPaid", "TaxPayableRecoverable",
        "Computers,Data & Software",
        "Plant & Machinery(Farming,Mining,Manufacture)",
        "Automobiles<=60Million",
        "Others not in any Class",
        "file"
    ]

    html = '''
    <h1>All Tax Records</h1>
    <button onclick="downloadCSV()">Download CSV</button>
    <br><br>
    <script>
    function toggle(id) {
        var x = document.getElementById(id);
        if (x.style.display === "none") { x.style.display = "block"; }
        else { x.style.display = "none"; }
    }
    function downloadCSV() {
        window.location.href = "/download_csv";
    }
    </script>
    '''

    for idx, row in enumerate(rows):
        html += f'''
        <div style="border:1px solid #333;padding:10px;margin-bottom:10px;">
            <button onclick="toggle('record{idx}')">Record {idx+1}</button>
            <div id="record{idx}" style="display:none;margin-top:10px;">
        '''
        for col, val in zip(columns, row[1:]):  # skip id
            if col == "file" and val:
                file_path = url_for('uploaded_file', filename=val)
                # Preview for images and PDFs
                if val.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    html += f'<b>{col}:</b> <br><img src="{file_path}" width="300"><br>'
                elif val.lower().endswith('.pdf'):
                    html += f'<b>{col}:</b> <br><iframe src="{file_path}" width="500" height="400"></iframe><br>'
                else:
                    html += f'<b>{col}:</b> <a href="{file_path}" target="_blank">{val}</a><br>'
            else:
                html += f'<b>{col}:</b> {val} <br>'
        html += '</div></div>'

    html += '<br><a href="/">Back to Form</a>'
    return html

@app.route('/download_csv')
def download_csv():
    conn = sqlite3.connect('tax_records.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tax_records')
    rows = c.fetchall()
    conn.close()

    columns = [
        "id", "FirmName", "Date_Period", "net_profit", "net_profit2", "Depreciation",
        "Bribes", "Penalties", "Gifts & Offers", "Donations", "Others",
        "Total Non Allowable Deductions", "Adjusted Net Profit Before Tax",
        "Total Wear & Tear2", "25% Start up Costs", "5% Industrial Building Deduction",
        "20% Initial Building Allowance", "Horticultural Exp", "Others NAD",
        "Total Allowable Deductions", "Chargeable Income", "Loss B/f",
        "Adjusted Chargeable Income", "30% Cooperation Tax", "WHTPaid",
        "TaxCredit", "ProvisionalTaxPaid", "TaxPayableRecoverable",
        "Computers,Data & Software",
        "Plant & Machinery(Farming,Mining,Manufacture)",
        "Automobiles<=60Million",
        "Others not in any Class",
        "file"
    ]

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(columns)
    cw.writerows(rows)
    output = si.getvalue()
    si.close()

    return app.response_class(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition':'attachment;filename=tax_records.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True)










