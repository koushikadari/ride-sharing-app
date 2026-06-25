from flask import Flask, request, jsonify
import math
import redis
import json
import os
import sys
sys.path.append('/app')

app = Flask(__name__)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

# In-memory driver locations for demo
DRIVER_LOCATIONS = {}

@app.route('/geo/location/driver/<driver_id>', methods=['POST'])
def update_driver_location(driver_id):
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    DRIVER_LOCATIONS[driver_id] = {
        'latitude': latitude,
        'longitude': longitude,
        'updated_at': data.get('timestamp')
    }
    
    # Store in Redis
    redis_client.set(
        f'driver_location:{driver_id}',
        json.dumps(DRIVER_LOCATIONS[driver_id])
    )
    
    return jsonify({'message': 'Location updated'}), 200

@app.route('/geo/location/driver/<driver_id>', methods=['GET'])
def get_driver_location(driver_id):
    location = redis_client.get(f'driver_location:{driver_id}')
    if location:
        return jsonify(json.loads(location)), 200
    return jsonify({'error': 'Driver location not found'}), 404

@app.route('/geo/location/nearby', methods=['GET'])
def find_nearby_drivers():
    rider_lat = float(request.args.get('latitude', 0))
    rider_lng = float(request.args.get('longitude', 0))
    radius = float(request.args.get('radius', 5))
    
    nearby_drivers = []
    for driver_id, location in DRIVER_LOCATIONS.items():
        distance = calculate_distance(
            rider_lat, rider_lng,
            location['latitude'], location['longitude']
        )
        if distance <= radius:
            nearby_drivers.append({
                'driver_id': driver_id,
                'distance': distance,
                'location': location
            })
    
    return jsonify({
        'drivers': sorted(nearby_drivers, key=lambda x: x['distance'])
    }), 200

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance using Haversine formula"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'geo-location'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
