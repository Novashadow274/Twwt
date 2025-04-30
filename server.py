from flask import Flask, jsonify
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    logger.info("Health check received")
    return 'Bot operational'

@app.route('/health')
def health():
    return jsonify({
        'status': 'active',
        'timestamp': datetime.now().isoformat(),
        'service': 'X-Twitter Scraper'
    })

@app.route('/ping')
def ping():
    return "pong", 200
