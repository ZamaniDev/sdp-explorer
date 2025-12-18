from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
from config import API_BASE_URL, API_KEY, ENDPOINTS

app = Flask(__name__)

# Request history for debugging
request_history = []

def api_call(method, endpoint, params=None, data=None):
    """Make API call to ME SDP MSP"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"authtoken": API_KEY}
    
    # Log request
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": method.upper(),
        "url": url,
        "params": params,
        "data": data,
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, verify=False)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, data=data, verify=False)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, data=data, verify=False)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, verify=False)
        
        # Log response
        log_entry["status_code"] = response.status_code
        log_entry["response"] = response.text
        request_history.append(log_entry)
        
        # Keep only last 50 requests
        if len(request_history) > 50:
            request_history.pop(0)
        
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json() if response.text else {},
            "raw": response.text
        }
    except Exception as e:
        log_entry["error"] = str(e)
        request_history.append(log_entry)
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/')
def index():
    """Main explorer page"""
    return render_template('explorer.html', endpoints=ENDPOINTS)

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test API connectivity"""
    result = api_call("GET", "/requests", params={
        'input_data': json.dumps({
            "list_info": {
                "row_count": 1,
                "start_index": 1,
                "get_total_count": True
            }
        })
    })
    return jsonify(result)

@app.route('/api/call', methods=['POST'])
def make_api_call():
    """Generic API call endpoint"""
    data = request.json
    method = data.get('method', 'GET')
    endpoint = data.get('endpoint', '')
    input_data = data.get('input_data', {})
    
    # Replace placeholders in endpoint
    placeholders = data.get('placeholders', {})
    for key, value in placeholders.items():
        endpoint = endpoint.replace(f"{{{key}}}", str(value))
    
    # Prepare request
    if method.upper() == "GET":
        params = {'input_data': json.dumps(input_data)} if input_data else None
        result = api_call(method, endpoint, params=params)
    else:
        data_param = {'input_data': json.dumps(input_data)} if input_data else None
        result = api_call(method, endpoint, data=data_param)
    
    return jsonify(result)

@app.route('/api/quick/requests', methods=['GET'])
def quick_requests():
    """Quick view: List recent requests"""
    result = api_call("GET", "/requests", params={
        'input_data': json.dumps({
            "list_info": {
                "row_count": 20,
                "start_index": 1,
                "sort_field": "created_time",
                "sort_order": "desc",
                "get_total_count": True
            }
        })
    })
    return jsonify(result)

@app.route('/api/quick/technicians', methods=['GET'])
def quick_technicians():
    """Quick view: List all technicians"""
    result = api_call("GET", "/technicians", params={
        'input_data': json.dumps({
            "list_info": {
                "row_count": 100,
                "start_index": 1,
                "get_total_count": True
            }
        })
    })
    return jsonify(result)

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get request history"""
    return jsonify(request_history)

if __name__ == '__main__':
    # Disable SSL warnings for self-signed certificates
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    app.run(debug=True, host='127.0.0.1', port=5000)