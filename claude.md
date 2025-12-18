# SDP Explorer - Project Overview

## Project Summary
A Flask-based web application for exploring and interacting with the ME SDP MSP (ManageEngine Service Desk Plus) API. Provides an intuitive interface for testing API endpoints, viewing responses, and managing service desk requests.

## Technology Stack
- **Backend**: Flask 3.0.0 (Python web framework)
- **HTTP Client**: requests 2.31.0
- **Frontend**: Vanilla JavaScript, HTML/CSS
- **API**: ManageEngine Service Desk Plus v3 REST API

## Project Structure
```
sdp-explorer/
├── app.py                 # Flask application with API routes
├── config.py              # API configuration and endpoint definitions
├── requirements.txt       # Python dependencies
├── templates/
│   ├── layout.html       # Base HTML template
│   └── explorer.html     # Main explorer interface
└── static/
    └── explorer.js       # Frontend JavaScript logic
```

## Key Features

### 1. API Connection Testing
- Quick connectivity test to verify API key validity
- Tests basic request endpoint functionality
- Located in `app.py:64-76` (test_connection route)

### 2. API Explorer
- **Category-based endpoint selection**: Organized by resource type (Requests, Users, Technicians, Notes, Worklogs, Reports)
- **Flexible input modes**:
  - Form mode with visual controls
  - Raw JSON mode for advanced usage
- **Smart response rendering**:
  - Card-based list views
  - Detailed modal views for individual items
  - JSON raw view option
- **Search and filtering**:
  - Dynamic field discovery from API responses
  - Multi-filter support with field path notation
  - Real-time result filtering

### 3. Quick Views
- Pre-configured views for common queries:
  - Recent requests (20 most recent)
  - All technicians list
- Switchable smart/JSON view modes

### 4. Request History
- Logs last 50 API requests
- Captures request/response details
- Debugging aid with full request/response inspection

### 5. Pagination Support
- Automatic pagination controls
- Tracks current page and total count
- Next/Previous navigation

## Configuration (`config.py`)

### API Settings
- **Base URL**: `https://support.pirasys.com/api/v3`
- **Authentication**: API key-based (authtoken header)
- **Current API Key**: `A38AFA8D-0DCD-440F-B8DC-759E5C9D3C3F`

### Defined Endpoints
The application supports the following endpoint categories:
- **Requests**: List, view, add, update, assign
- **Notes**: List, view, add notes to requests
- **Users**: List and view users
- **Technicians**: List and view technicians
- **Worklogs**: Request worklogs and summaries
- **Reports**: List, execute reports and queries

## Core Functionality

### API Call Handler (`app.py:12-57`)
- Centralized API communication function
- Handles GET, POST, PUT, DELETE methods
- SSL verification disabled for self-signed certificates
- Automatic request/response logging
- Error handling with detailed error messages

### Smart Response Renderer (`static/explorer.js:455-740`)
- Intelligent detection of response structure
- Automatic identification of lists vs single objects
- Preview field selection based on field importance:
  - ID fields (request_id, ticket_id, user_id)
  - Name/title fields
  - Status/priority badges with colors
  - Timestamps
  - Person fields (requester, technician)

### Dynamic Field Discovery (`static/explorer.js:195-295`)
- Analyzes API response structure
- Extracts filterable field paths
- Groups fields by category
- Enables click-to-add filter functionality
- Handles nested objects (e.g., `status.name`, `requester.id`)

### Search Filter System
- Supports dot notation for nested fields
- Multiple filters with AND logic
- Dynamic filter management (add/remove)
- Integrates with ME SDP API's `search_fields` parameter

## API Integration Details

### Request Format
GET requests use query parameters:
```python
params = {
    'input_data': json.dumps({
        'list_info': {
            'row_count': 20,
            'start_index': 1,
            'sort_field': 'created_time',
            'sort_order': 'desc',
            'get_total_count': True,
            'search_fields': {
                'status.name': 'Open',
                'priority.name': 'High'
            }
        }
    })
}
```

POST/PUT requests use form data:
```python
data = {
    'input_data': json.dumps({
        # request body
    })
}
```

### Authentication
All requests include:
```python
headers = {"authtoken": API_KEY}
```

### Response Structure
Standard ME SDP API response format:
```json
{
    "list_info": {
        "total_count": 100,
        "has_more_rows": true,
        "start_index": 1,
        "row_count": 20
    },
    "requests": [
        {
            "id": "12345",
            "subject": "Request subject",
            "status": {"name": "Open", "color": "#00ff00"},
            "requester": {"name": "John Doe", "id": "123"}
        }
    ]
}
```

## Running the Application

### Setup
```bash
pip install -r requirements.txt
```

### Start Server
```bash
python app.py
```

Access at: `http://127.0.0.1:5000`

### Debug Mode
Enabled by default in `app.py:141`:
```python
app.run(debug=True, host='127.0.0.1', port=5000)
```

## Security Considerations

### Current Security Issues
1. **Hardcoded API Key**: API key is stored in `config.py` (should use environment variables)
2. **SSL Verification Disabled**: `verify=False` in requests (security risk)
3. **No Rate Limiting**: No throttling on API calls
4. **No Authentication**: Web interface has no user authentication
5. **Debug Mode in Production**: Should be disabled for production deployment

### Recommended Improvements
- Move API credentials to environment variables
- Enable SSL verification with proper certificate handling
- Add web application authentication
- Implement rate limiting
- Disable debug mode for production

## Development Notes

### URL Placeholder Replacement
The application supports dynamic URL parameters using `{placeholder}` syntax:
- Example: `/requests/{request_id}`
- Replaced in `app.py:86-89` before making API call

### Request History Management
- Stored in-memory (lost on restart)
- Limited to 50 most recent requests
- Could be persisted to database for long-term storage

### Frontend State Management
Global JavaScript state variables (`static/explorer.js:3-14`):
- `endpoints`: Endpoint configuration from backend
- `lastResponse`: Most recent API response
- `currentPage`: Pagination tracking
- `discoveredFields`: Cached filterable fields

## API Endpoint Reference

### Requests
- **GET** `/requests` - List all requests
- **GET** `/requests/{request_id}` - View specific request
- **POST** `/requests` - Create new request
- **PUT** `/requests/{request_id}` - Update request
- **POST** `/requests/{request_id}/assign` - Assign request

### Notes
- **GET** `/requests/{request_id}/notes` - List notes
- **GET** `/requests/{request_id}/notes/{note_id}` - View note
- **POST** `/requests/{request_id}/notes` - Add note

### Users & Technicians
- **GET** `/users` - List users
- **GET** `/users/{user_id}` - View user
- **GET** `/technicians` - List technicians
- **GET** `/technicians/{technician_id}` - View technician

### Worklogs
- **GET** `/requests/{request_id}/worklogs` - List worklogs
- **GET** `/requests/{request_id}/worklogs/summary` - Worklog summary

### Reports
- **GET** `/reports` - List available reports
- **POST** `/reports/{report_id}/execute` - Execute report
- **POST** `/reports/execute_query` - Execute custom query

## Future Enhancement Ideas
- User authentication system
- Saved queries/favorites
- Export to CSV/Excel
- Bulk operations support
- Webhook configuration
- Custom report builder
- Dark mode UI
- Request templates
- Attachment upload/download
- Email notifications integration
