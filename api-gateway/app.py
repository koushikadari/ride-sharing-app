from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SERVICES = {
    'auth': os.getenv('AUTH_SERVICE_URL', 'http://auth:5001'),
    'rider': os.getenv('RIDER_SERVICE_URL', 'http://rider:5002'),
    'driver': os.getenv('DRIVER_SERVICE_URL', 'http://driver:5003'),
    'matching': os.getenv('MATCHING_SERVICE_URL', 'http://matching:5004'),
    'trip': os.getenv('TRIP_SERVICE_URL', 'http://trip:5005'),
    'payment': os.getenv('PAYMENT_SERVICE_URL', 'http://payment:5006'),
    'geo': os.getenv('GEO_SERVICE_URL', 'http://geo-location:5007'),
}

@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(service, path):
    if service not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404
    
    target_url = f"{SERVICES[service]}/{path}"
    
    try:
        headers = {key: value for key, value in request.headers.items() 
                  if key.lower() not in ['host', 'content-length']}
        
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            json=request.json if request.is_json else None,
            params=request.args,
            timeout=30
        )
        
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Service unavailable: {str(e)}'}), 503

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'services': list(SERVICES.keys())}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
