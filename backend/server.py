from flask import Flask, jsonify
from flask_cors import CORS
import sys

app = Flask(__name__)
CORS(app)

# Get the port from command line arguments or use default
port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Backend server says: HELLO WORLD!"})

if __name__ == '__main__':
    app.run(host='localhost', port=port)