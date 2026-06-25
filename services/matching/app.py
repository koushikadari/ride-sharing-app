from flask import Flask, request, jsonify
import redis
import json
import requests
import os
import sys
sys.path.append('/app')
from shared.models import Trip, RideStatus, Location
from shared.utils import generate_id

app = Flask(__name__)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

GEO_SERVICE_URL = os.getenv('GEO_SERVICE_URL', 'http://geo-location:5007')
TRIP_SERVICE_URL = os.getenv('TRIP_SERVICE_URL', 'http://trip:5005')

@app.route('/matching/find', methods=['POST'])
def find_drivers():
    data = request.json
    rider_id = data.get('rider_id')
    pickup = data.get('pickup_location')
    radius = data.get('radius', 5)
    
    # Find nearby drivers from geo-location service
    response = requests.get(
        f'{GEO_SERVICE_URL}/geo/location/nearby',
        params={
            'latitude': pickup['latitude'],
            'longitude': pickup['longitude'],
            'radius': radius
        }
    )
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to find nearby drivers'}), 500
    
    drivers = response.json().get('drivers', [])
    
    # Store matching request
    match_id = generate_id()
    matching_data = {
        'match_id': match_id,
        'rider_id': rider_id,
        'pickup_location': pickup,
        'dropoff_location': data.get('dropoff_location'),
        'available_drivers': drivers[:5],
        'status': 'pending'
    }
    
    redis_client.setex(
        f'matching:{match_id}',
        300,
        json.dumps(matching_data)
    )
    
    return jsonify({
        'match_id': match_id,
        'drivers': drivers[:5]
    }), 200

@app.route('/matching/accept/<match_id>/<driver_id>', methods=['POST'])
def accept_ride(match_id, driver_id):
    matching_data = redis_client.get(f'matching:{match_id}')
    if not matching_data:
        return jsonify({'error': 'Matching request expired'}), 404
    
    data = json.loads(matching_data)
    
    # Create trip
    trip = Trip(
        id=generate_id(),
        rider_id=data['rider_id'],
        driver_id=driver_id,
        pickup_location=Location(**data['pickup_location']),
        dropoff_location=Location(**data['dropoff_location']),
        status=RideStatus.ACCEPTED
    )
    
    # Create trip via trip service
    response = requests.post(
        f'{TRIP_SERVICE_URL}/trips',
        json=trip.dict()
    )
    
    if response.status_code != 201:
        return jsonify({'error': 'Failed to create trip'}), 500
    
    # Update matching status
    data['status'] = 'accepted'
    data['driver_id'] = driver_id
    redis_client.setex(f'matching:{match_id}', 300, json.dumps(data))
    
    return jsonify({'trip': response.json()}), 201

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'matching'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
