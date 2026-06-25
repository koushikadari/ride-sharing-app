from flask import Flask, request, jsonify
import redis
import json
from datetime import datetime
import sys
import os
sys.path.append('/app')
from shared.models import Trip, RideStatus
from shared.utils import generate_id

app = Flask(__name__)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

# In-memory trip storage for demo
TRIPS = {}

@app.route('/trips', methods=['POST'])
def create_trip():
    data = request.json
    trip = Trip(
        id=generate_id(),
        rider_id=data['rider_id'],
        driver_id=data.get('driver_id'),
        pickup_location=data['pickup_location'],
        dropoff_location=data['dropoff_location'],
        status=RideStatus.REQUESTED
    )
    
    TRIPS[trip.id] = trip.dict()
    redis_client.setex(f'trip:{trip.id}', 86400, json.dumps(trip.dict()))
    
    return jsonify(trip.dict()), 201

@app.route('/trips/<trip_id>', methods=['GET'])
def get_trip(trip_id):
    trip = redis_client.get(f'trip:{trip_id}')
    if trip:
        return jsonify(json.loads(trip)), 200
    return jsonify({'error': 'Trip not found'}), 404

@app.route('/trips/<trip_id>/status', methods=['PUT'])
def update_trip_status(trip_id):
    data = request.json
    new_status = data.get('status')
    
    trip_data = redis_client.get(f'trip:{trip_id}')
    if not trip_data:
        return jsonify({'error': 'Trip not found'}), 404
    
    trip = json.loads(trip_data)
    trip['status'] = new_status
    trip['updated_at'] = datetime.utcnow().isoformat()
    
    redis_client.setex(f'trip:{trip_id}', 86400, json.dumps(trip))
    TRIPS[trip_id] = trip
    
    return jsonify(trip), 200

@app.route('/trips/driver/<driver_id>', methods=['GET'])
def get_driver_trips(driver_id):
    trips = [t for t in TRIPS.values() if t['driver_id'] == driver_id]
    return jsonify(trips), 200

@app.route('/trips/rider/<rider_id>', methods=['GET'])
def get_rider_trips(rider_id):
    trips = [t for t in TRIPS.values() if t['rider_id'] == rider_id]
    return jsonify(trips), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'trip'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
