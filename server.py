from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot operational'

@app.route('/health')
def health():
    return jsonify({
        'status': 'active',
        'timestamp': datetime.now().isoformat()
    })
