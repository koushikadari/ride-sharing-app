from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import redis
import json
import requests
import os
import sys
sys.path.append('/app')
from shared.models import UserRole

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret-key')
jwt = JWTManager(app)

redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

# Service URLs - will be configured via environment variables
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth:5001')
MATCHING_SERVICE_URL = os.getenv('MATCHING_SERVICE_URL', 'http://matching:5004')
TRIP_SERVICE_URL = os.getenv('TRIP_SERVICE_URL', 'http://trip:5005')

@app.route('/rider/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_email = get_jwt_identity()
    user_data = redis_client.get(f'session:{current_user_email}')
    if user_data:
        user = json.loads(user_data)
        if user['role'] != UserRole.RIDER.value:
            return jsonify({'error': 'Unauthorized'}), 403
        return jsonify(user), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/rider/request-ride', methods=['POST'])
@jwt_required()
def request_ride():
    current_user_email = get_jwt_identity()
    user_data = redis_client.get(f'session:{current_user_email}')
    if not user_data:
        return jsonify({'error': 'User not authenticated'}), 401
    
    user = json.loads(user_data)
    data = request.json
    
    # Call matching service
    response = requests.post(
        f'{MATCHING_SERVICE_URL}/matching/find',
        json={
            'rider_id': user['id'],
            'pickup_location': data['pickup_location'],
            'dropoff_location': data['dropoff_location'],
            'radius': data.get('radius', 5)
        }
    )
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to find drivers'}), 500
    
    return jsonify(response.json()), 200

@app.route('/rider/trips', methods=['GET'])
@jwt_required()
def get_rider_trips():
    current_user_email = get_jwt_identity()
    user_data = redis_client.get(f'session:{current_user_email}')
    if not user_data:
        return jsonify({'error': 'User not authenticated'}), 401
    
    user = json.loads(user_data)
    
    response = requests.get(f'{TRIP_SERVICE_URL}/trips/rider/{user["id"]}')
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch trips'}), 500
    
    return jsonify(response.json()), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'rider'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
