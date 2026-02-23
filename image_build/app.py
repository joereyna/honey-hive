import sqlite3
import os
from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError, validator

API_KEY = os.environ.get('API_KEY')

AWS_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1", "ap-southeast-2", "ap-northeast-2", "sa-east-1"
]

# Validate service schema
class ServiceModel(BaseModel):
    name: str
    region: str
    host: str
    port: int
    healthEndpoint: str

    @validator('region')
    def region_must_be_valid(cls, v):
        if v not in AWS_REGIONS:
            raise ValueError(f"region must be a valid AWS region, got '{v}'")
        return v

app = Flask(__name__)

DB_PATH = 'services.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        region TEXT NOT NULL,
        host TEXT NOT NULL,
        port INTEGER NOT NULL,
        healthEndpoint TEXT NOT NULL,
        registered_at TEXT DEFAULT (datetime('now')),
        UNIQUE(name, region)
    )''')
    conn.commit()
    conn.close()

init_db()

# Require API key for all requests
@app.before_request
def require_api_key():
    if request.headers.get('x-api-key') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

@app.route('/api/v1/regions', methods=['GET'])
def regions():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT DISTINCT region FROM services')
    rows = c.fetchall()
    conn.close()
    region_list = [row[0] for row in rows]
    return {"regions": region_list}

@app.route('/api/v1/regions/<string:region>/services', methods=['GET'])
def get_services_by_region(region):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, host, port, healthEndpoint FROM services WHERE region = ?', (region,))
    rows = c.fetchall()
    if not rows:
        conn.close()
        return jsonify({"error": "No services found for this region"}), 404
    conn.close()
    services_list = [
        {"id": row[0], "name": row[1], "host": row[2], "port": row[3], "healthEndpoint": row[4]}
        for row in rows
    ]
    return {"services": services_list}

@app.route('/api/v1/services', methods=['POST'])
def services():
    try:
        data = request.json
        service = ServiceModel(**data)
    except ValidationError as e:
        return jsonify({
            "error": "Invalid input",
            "details": e.errors()
        }), 400
    new_service = service.dict()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, registered_at FROM services WHERE name = ? AND region = ?', (new_service['name'], new_service['region']))
    row = c.fetchone()
    if row:
        service_id = row[0]
        registered_at = row[1]
        c.execute('UPDATE services SET host = ?, port = ?, healthEndpoint = ? WHERE id = ?',
                  (new_service['host'], new_service['port'], new_service['healthEndpoint'], service_id))
        conn.commit()
        c.execute('SELECT id, name, region, host, port, healthEndpoint, registered_at FROM services WHERE id = ?', (service_id,))
        updated = c.fetchone()
        conn.close()
        updated_service = {
            "id": updated[0],
            "name": updated[1],
            "region": updated[2],
            "host": updated[3],
            "port": updated[4],
            "healthEndpoint": updated[5],
            "registered_at": updated[6]
        }
        return {"message": "Service updated", "service": updated_service}, 200
    else:
        c.execute('INSERT INTO services (name, region, host, port, healthEndpoint, registered_at) VALUES (?, ?, ?, ?, ?, datetime("now"))',
                  (new_service['name'], new_service['region'], new_service['host'], new_service['port'], new_service['healthEndpoint']))
        conn.commit()
        new_id = c.lastrowid
        c.execute('SELECT id, name, region, host, port, healthEndpoint, registered_at FROM services WHERE id = ?', (new_id,))
        created = c.fetchone()
        conn.close()
        created_service = {
            "id": created[0],
            "name": created[1],
            "region": created[2],
            "host": created[3],
            "port": created[4],
            "healthEndpoint": created[5],
            "registered_at": created[6]
        }
        return {"message": "Service created", "service": created_service}, 201


@app.route('/api/v1/services/<int:id>', methods=['DELETE'])
def delete_service(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM services WHERE id = ?', (id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Service not found"}), 404
    c.execute('DELETE FROM services WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return '', 204

@app.route('/')
def hello_world():
    return 'Hello, HoneyHive!'

# Populate example data for demo purposes
def populate_example_data():
    example_services = [
        {
            "name": "backend",
            "region": "us-east-1",
            "host": "10.0.0.1",
            "port": 8080,
            "healthEndpoint": "/checks/health"
        },
        {
            "name": "frontend",
            "region": "us-west-2",
            "host": "10.0.0.2",
            "port": 80,
            "healthEndpoint": "/checks/health"
        },
        {
            "name": "worker",
            "region": "eu-west-1",
            "host": "10.0.0.3",
            "port": 9000,
            "healthEndpoint": "/checks/health"
        }
    ]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for svc in example_services:
        try:
            service = ServiceModel(**svc)
            c.execute('SELECT id FROM services WHERE name = ? AND region = ?', (svc['name'], svc['region']))
            if not c.fetchone():
                c.execute('INSERT INTO services (name, region, host, port, healthEndpoint) VALUES (?, ?, ?, ?, ?)',
                          (svc['name'], svc['region'], svc['host'], svc['port'], svc['healthEndpoint']))
        except Exception as e:
            print(f"Skipping invalid service: {svc} ({e})")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    populate_example_data()
    app.run(host='0.0.0.0', port=5000)