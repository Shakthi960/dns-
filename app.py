from flask import Flask, request, jsonify, render_template, redirect, url_for
import csv, io
from blockchain import SimpleChain
from safecheck import domain_is_safe

app = Flask(__name__)
chain = SimpleChain()

@app.route('/')
def index():
    records = chain.all_records()
    return render_template('index.html', records=records)

@app.route('/import_csv', methods=['POST'])
def import_csv():
    f = request.files.get('file')
    if not f:
        return 'No file', 400
    s = f.read().decode()
    reader = csv.reader(io.StringIO(s))
    added = []
    for row in reader:
        if len(row) >= 2:
            domain, ip = row[0].strip(), row[1].strip()
            safe, meta = domain_is_safe(domain)
            rec = {
                'domain': domain,
                'ip': ip,
                'added_by': 'csv',
                'safety': 1.0 if safe else 0.0,
                'meta': meta
            }
            added.append(rec)
    chain.add_block(added)
    return redirect(url_for('index'))

@app.route('/add_domain', methods=['POST'])
def add_domain():
    domain = request.form.get('domain')
    ip = request.form.get('ip')
    if not domain or not ip:
        return 'missing', 400
    safe, meta = domain_is_safe(domain)
    rec = {
        'domain': domain,
        'ip': ip,
        'added_by': 'ui',
        'safety': 1.0 if safe else 0.0,
        'meta': meta
    }
    chain.add_block([rec])
    return redirect(url_for('index'))

# Simple DNS-over-HTTPS (DoH)-like endpoint
@app.route('/dns-query', methods=['GET'])
def doh_query():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'missing name param'}), 400
    records = chain.all_records()
    rec = records.get(name.lower())
    if not rec or rec.get('safety', 0.0) < 0.5:
        return jsonify({'Status': 'NXDOMAIN'}), 404
    return jsonify({'Status': 'NOERROR', 'Answer': {'name': name, 'ip': rec['ip']}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
