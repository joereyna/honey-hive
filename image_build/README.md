# HoneyHiveAI Service Registry Demo

This is a simple demo API for registering and managing service instances, built with Flask, Pydantic, and SQLite3. The API enforces schema validation and uses an API key for authentication.

## Features
- Register, update (upsert), and delete service instances
- Query all regions and services per region
- Enforces required fields and valid AWS regions
- Uses SQLite3 for persistent storage (file-based, no external DB needed)
- Demo data is loaded into the database on every startup

## Database Initialization
Every time the app starts, the SQLite database (`services.db`) is initialized and populated with example service data. This ensures a consistent demo environment and makes it easy to reset the state by simply restarting the app or container.

## Running Locally
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Set your API key:
   ```sh
   export API_KEY=your-generated-api-key
   ```
3. Run the app:
   ```sh
   python app.py
   ```

## Running with Docker
1. Build the image:
   ```sh
   docker build -t honeyhiveai .
   ```
2. Run the container (using port 5000):
   ```sh
   docker run -p 5000:5000 -e API_KEY=your-generated-api-key honeyhiveai
   ```

## Example Usage
Assuming you have exported your API key:
```sh
export API_KEY=your-generated-api-key
```

### Register a new service
```sh
curl -X POST http://127.0.0.1:5000/api/v1/services \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"name": "api", "region": "us-east-1", "host": "10.0.0.4", "port": 5000, "healthEndpoint": "/checks/health"}'
```

### Get all regions
```sh
curl -X GET -H "X-API-Key: $API_KEY" http://127.0.0.1:5000/api/v1/regions
```

### Get all services in a region
```sh
curl -X GET -H "X-API-Key: $API_KEY" http://127.0.0.1:5000/api/v1/regions/us-east-1/services
```

### Delete a service by ID
```sh
curl -X DELETE -H "X-API-Key: $API_KEY" http://127.0.0.1:5000/api/v1/services/1
```

---

This project is for demo purposes only. For production, use a real database, secure your API key, and run Flask behind a production WSGI server.
