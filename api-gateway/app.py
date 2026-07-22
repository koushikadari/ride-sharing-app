from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Service URLs
services = {
    'auth': os.getenv('AUTH_SERVICE_URL', 'http://auth:5001'),
    'rider': os.getenv('RIDER_SERVICE_URL', 'http://rider:5002'),
    'driver': os.getenv('DRIVER_SERVICE_URL', 'http://driver:5003'),
    'matching': os.getenv('MATCHING_SERVICE_URL', 'http://matching:5004'),
    'trip': os.getenv('TRIP_SERVICE_URL', 'http://trip:5005'),
    'payment': os.getenv('PAYMENT_SERVICE_URL', 'http://payment:5006'),
    'geo': os.getenv('GEO_SERVICE_URL', 'http://geo-location:5007')
}


# Home route
@app.route('/')
def home():
    return jsonify({
        "application": "Ride Sharing API Gateway",
        "status": "running",
        "message": "API Gateway is working",
        "services": list(services.keys())
    })


# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "services": list(services.keys())
    })


# Dynamic routing
@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway(service, path):

    if service not in services:
        return jsonify({
            "error": "Service not found"
        }), 404

    url = f"{services[service]}/{path}"

    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            json=request.get_json(silent=True)
        )

        return (
            response.text,
            response.status_code,
            {'Content-Type': response.headers.get('Content-Type')}
        )

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000
    )
