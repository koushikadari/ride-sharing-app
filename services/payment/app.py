from flask import Flask, request, jsonify
import redis
import json
import random
import sys
import os
sys.path.append('/app')
from shared.models import Payment, PaymentStatus
from shared.utils import generate_id

app = Flask(__name__)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

PAYMENTS = {}

@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.json
    payment = Payment(
        id=generate_id(),
        trip_id=data['trip_id'],
        rider_id=data['rider_id'],
        amount=data['amount'],
        payment_method=data['payment_method'],
        status=PaymentStatus.PENDING
    )
    
    PAYMENTS[payment.id] = payment.dict()
    redis_client.setex(f'payment:{payment.id}', 86400, json.dumps(payment.dict()))
    
    return jsonify(payment.dict()), 201

@app.route('/payments/<payment_id>/process', methods=['POST'])
def process_payment(payment_id):
    payment_data = redis_client.get(f'payment:{payment_id}')
    if not payment_data:
        return jsonify({'error': 'Payment not found'}), 404
    
    payment = json.loads(payment_data)
    
    # Simulate payment processing
    success = random.choice([True, False])
    
    if success:
        payment['status'] = PaymentStatus.COMPLETED.value
        payment['transaction_id'] = f'TXN{generate_id()[:8]}'
    else:
        payment['status'] = PaymentStatus.FAILED.value
    
    redis_client.setex(f'payment:{payment_id}', 86400, json.dumps(payment))
    PAYMENTS[payment_id] = payment
    
    return jsonify(payment), 200

@app.route('/payments/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = redis_client.get(f'payment:{payment_id}')
    if payment:
        return jsonify(json.loads(payment)), 200
    return jsonify({'error': 'Payment not found'}), 404

@app.route('/payments/trip/<trip_id>', methods=['GET'])
def get_payment_by_trip(trip_id):
    payments = [p for p in PAYMENTS.values() if p['trip_id'] == trip_id]
    return jsonify(payments), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'payment'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
