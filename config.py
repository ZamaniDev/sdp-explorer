# Configuration for ME SDP MSP API
API_BASE_URL = "https://support.pirasys.com/api/v3"
API_KEY = "A38AFA8D-0DCD-440F-B8DC-759E5C9D3C3F"

# Common endpoints (we'll expand this)
ENDPOINTS = {
    "Requests": {
        "list": "/requests",
        "view": "/requests/{request_id}",
        "add": "/requests",
        "update": "/requests/{request_id}",
        "assign": "/requests/{request_id}/assign",
    },
    "Notes": {
        "list": "/requests/{request_id}/notes",
        "view": "/requests/{request_id}/notes/{note_id}",
        "add": "/requests/{request_id}/notes",
    },
    "Users": {
        "list": "/users",
        "view": "/users/{user_id}",
    },
    "Technicians": {
        "list": "/technicians",
        "view": "/technicians/{technician_id}",
    },
    "Worklogs": {
        "request_list": "/requests/{request_id}/worklogs",
        "request_summary": "/requests/{request_id}/worklogs/summary",
    },
    "Reports": {
        "list": "/reports",
        "execute": "/reports/{report_id}/execute",
        "execute_query": "/reports/execute_query",
    },
    "Accounts": {
        "list": "/accounts",
        "view": "/accounts/{account_id}",
        "add": "/accounts",
        "update": "/accounts/{account_id}",
        "delete": "/accounts/{account_id}",
        "search": "/accounts",
        "contacts": "/accounts/{account_id}/contacts",
        "sites": "/accounts/{account_id}/sites",
    }
}