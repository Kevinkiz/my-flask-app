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
            "GiftsAndOffers" REAL,
            "Donations" REAL,
            "Others" REAL,
            "TotalNonAllowableDeductions" REAL,
            "AdjustedNetProfitBeforeTax" REAL,
            "TotalWearAndTear2" REAL,
            "StartupCosts" REAL,
            "IndustrialBuildingDeduction" REAL,
            "InitialBuildingAllowance" REAL,
            "HorticulturalExp" REAL,
            "OthersNAD" REAL,
            "TotalAllowableDeductions" REAL,
            "ChargeableIncome" REAL,
            "LossBf" REAL,
            "AdjustedChargeableIncome" REAL,
            "CooperationTax" REAL,
            "WHTPaid" REAL,
            "TaxCredit" REAL,
            "ProvisionalTaxPaid" REAL,
            "TaxPayableRecoverable" REAL,
            "ComputersDataSoftware" REAL,
            "PlantMachinery" REAL,
            "Automobiles" REAL,
            "OthersNotInClass" REAL,
            "file" TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper to safely convert to float
def to_float(form, field):
    try:
        value = form.get(field, "0") or "0"
        # Remove commas and spaces before converting
        value = value.replace(",", "").strip()
        return float(value)
    except Exception:
        return 0.0


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
            "Bribes", "Penalties", "GiftsAndOffers", "Donations", "Others",
            "TotalNonAllowableDeductions", "AdjustedNetProfitBeforeTax",
            "TotalWearAndTear2", "StartupCosts", "IndustrialBuildingDeduction",
            "InitialBuildingAllowance", "HorticulturalExp", "OthersNAD",
            "TotalAllowableDeductions", "ChargeableIncome", "LossBf",
            "AdjustedChargeableIncome", "CooperationTax", "WHTPaid",
            "TaxCredit", "ProvisionalTaxPaid", "TaxPayableRecoverable",
            "ComputersDataSoftware",
            "PlantMachinery",
            "Automobiles",
            "OthersNotInClass",
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
        to_float(form, 'GiftsAndOffers'),
        to_float(form, 'Donations'),
        to_float(form, 'Others'),
        to_float(form, 'TotalNonAllowableDeductions'),
        to_float(form, 'AdjustedNetProfitBeforeTax'),
        to_float(form, 'TotalWearAndTear2'),
        to_float(form, 'StartupCosts'),
        to_float(form, 'IndustrialBuildingDeduction'),
        to_float(form, 'InitialBuildingAllowance'),
        to_float(form, 'HorticulturalExp'),
        to_float(form, 'OthersNAD'),
        to_float(form, 'TotalAllowableDeductions'),
        to_float(form, 'ChargeableIncome'),
        to_float(form, 'LossBf'),
        to_float(form, 'AdjustedChargeableIncome'),
        to_float(form, 'CooperationTax'),
        to_float(form, 'WHTPaid'),
        to_float(form, 'TaxCredit'),
        to_float(form, 'ProvisionalTaxPaid'),
        to_float(form, 'TaxPayableRecoverable'),
        to_float(form, 'ComputersDataSoftware'),
        to_float(form, 'PlantMachinery'),
        to_float(form, 'Automobiles'),
        to_float(form, 'OthersNotInClass'),
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
        "Bribes", "Penalties", "GiftsAndOffers", "Donations", "Others",
        "TotalNonAllowableDeductions", "AdjustedNetProfitBeforeTax",
        "TotalWearAndTear2", "StartupCosts", "IndustrialBuildingDeduction",
        "InitialBuildingAllowance", "HorticulturalExp", "OthersNAD",
        "TotalAllowableDeductions", "ChargeableIncome", "LossBf",
        "AdjustedChargeableIncome", "CooperationTax", "WHTPaid",
        "TaxCredit", "ProvisionalTaxPaid", "TaxPayableRecoverable",
        "ComputersDataSoftware",
        "PlantMachinery",
        "Automobiles",
        "OthersNotInClass",
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
        "Bribes", "Penalties", "GiftsAndOffers", "Donations", "Others",
        "TotalNonAllowableDeductions", "AdjustedNetProfitBeforeTax",
        "TotalWearAndTear2", "StartupCosts", "IndustrialBuildingDeduction",
        "InitialBuildingAllowance", "HorticulturalExp", "OthersNAD",
        "TotalAllowableDeductions", "ChargeableIncome", "LossBf",
        "AdjustedChargeableIncome", "CooperationTax", "WHTPaid",
        "TaxCredit", "ProvisionalTaxPaid", "TaxPayableRecoverable",
        "ComputersDataSoftware",
        "PlantMachinery",
        "Automobiles",
        "OthersNotInClass",
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











