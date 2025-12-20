"""
Test script for ME SDP Accounts API endpoints

This script helps you test the accounts endpoints and see example requests/responses.
Run this after logging into the SDP Explorer web interface.
"""

import requests
import json
from config import API_BASE_URL, API_KEY

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def api_call(method, endpoint, data=None):
    """Make API call to ME SDP"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"authtoken": API_KEY}

    print(f"\n{'='*60}")
    print(f"{method} {endpoint}")
    print(f"{'='*60}")

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data, verify=False)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=data, verify=False)
        elif method == "PUT":
            response = requests.put(url, headers=headers, data=data, verify=False)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, verify=False)

        print(f"Status Code: {response.status_code}")

        if response.text:
            result = response.json()
            print(f"Response:")
            print(json.dumps(result, indent=2)[:500])  # First 500 chars
            return result
        else:
            print("No response body")
            return None

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def test_accounts_endpoints():
    """Test various accounts endpoints"""

    print("\n" + "="*60)
    print("TESTING ACCOUNTS ENDPOINTS")
    print("="*60)

    # 1. List all accounts
    print("\n\n1. LIST ALL ACCOUNTS")
    print("-" * 60)
    list_params = {
        'input_data': json.dumps({
            "list_info": {
                "row_count": 10,
                "start_index": 1,
                "get_total_count": True
            }
        })
    }
    accounts_list = api_call("GET", "/accounts", data=list_params)

    # Extract first account ID if available
    account_id = None
    if accounts_list and 'accounts' in accounts_list:
        accounts = accounts_list.get('accounts', [])
        if accounts:
            account_id = accounts[0].get('id')
            print(f"\nFound {len(accounts)} accounts")
            print(f"First account ID: {account_id}")

    # 2. Get specific account (if we found one)
    if account_id:
        print("\n\n2. GET SPECIFIC ACCOUNT")
        print("-" * 60)
        api_call("GET", f"/accounts/{account_id}")

        print("\n\n3. GET ACCOUNT CONTACTS")
        print("-" * 60)
        contacts_params = {
            'input_data': json.dumps({
                "list_info": {
                    "row_count": 10
                }
            })
        }
        api_call("GET", f"/accounts/{account_id}/contacts", data=contacts_params)

        print("\n\n4. GET ACCOUNT SITES")
        print("-" * 60)
        sites_params = {
            'input_data': json.dumps({
                "list_info": {
                    "row_count": 10
                }
            })
        }
        api_call("GET", f"/accounts/{account_id}/sites", data=sites_params)

    # 3. Search accounts
    print("\n\n5. SEARCH ACCOUNTS (by name)")
    print("-" * 60)
    search_params = {
        'input_data': json.dumps({
            "list_info": {
                "row_count": 10,
                "search_fields": {
                    "name": "test"  # Search for accounts with "test" in name
                }
            }
        })
    }
    api_call("GET", "/accounts", data=search_params)

    print("\n\n" + "="*60)
    print("EXAMPLE: CREATE NEW ACCOUNT")
    print("="*60)
    print("""
To create a new account via the web interface:

1. Go to the API Explorer
2. Select "Accounts" category
3. Choose "add" endpoint
4. Use this JSON in the input_data:

{
  "account": {
    "name": "Test Company Inc",
    "website": "https://testcompany.com",
    "phone": "+1-555-0100",
    "fax": "+1-555-0101",
    "account_type": {
      "name": "Customer"
    },
    "industry": {
      "name": "Technology"
    },
    "address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "zip_code": "94105",
      "country": "USA"
    },
    "description": "Test account created via API"
  }
}
    """)

    print("\n\n" + "="*60)
    print("EXAMPLE: UPDATE ACCOUNT")
    print("="*60)
    print(f"""
To update an account via the web interface:

1. Go to the API Explorer
2. Select "Accounts" category
3. Choose "update" endpoint
4. Set placeholder account_id = {account_id or 'YOUR_ACCOUNT_ID'}
5. Use this JSON in the input_data:

{{
  "account": {{
    "name": "Updated Company Name",
    "phone": "+1-555-9999",
    "description": "Updated description"
  }}
}}
    """)

    print("\n\n" + "="*60)
    print("API PERMISSIONS REQUIRED")
    print("="*60)
    print("""
Accounts endpoints require different permission levels:

READ Operations (Technician or Admin):
  - GET /accounts (list)
  - GET /accounts/{id} (view)
  - GET /accounts/{id}/contacts
  - GET /accounts/{id}/sites

WRITE Operations (Admin required):
  - POST /accounts (create)
  - PUT /accounts/{id} (update)
  - DELETE /accounts/{id} (delete)

Make sure your API key has the appropriate permissions!
    """)


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║         ME SDP Accounts API Endpoint Tester                  ║
║                                                              ║
║  This script will test the accounts endpoints and show      ║
║  you example requests and responses.                        ║
╚══════════════════════════════════════════════════════════════╝
    """)

    response = input("\nPress Enter to start testing, or 'q' to quit: ")
    if response.lower() != 'q':
        test_accounts_endpoints()

        print("\n\n" + "="*60)
        print("TESTING COMPLETE")
        print("="*60)
        print("\nYou can now use these endpoints in the SDP Explorer web interface!")
        print("Navigate to http://127.0.0.1:5000 and select 'Accounts' from the category dropdown.")
