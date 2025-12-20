# ME SDP Accounts API Reference

## Overview

The Accounts API allows you to manage customer/organization accounts in ManageEngine Service Desk Plus. Accounts represent companies, organizations, or business entities that submit service requests.

## Base URL
```
https://support.pirasys.com/api/v3
```

## Authentication
All requests require an `authtoken` header with a valid API key.

---

## Endpoints

### 1. List All Accounts

**Endpoint:** `GET /accounts`

**Permission Required:** Technician or Admin

**Description:** Retrieve a list of all accounts with pagination and filtering support.

**Request Example:**
```json
{
  "list_info": {
    "row_count": 25,
    "start_index": 1,
    "sort_field": "name",
    "sort_order": "asc",
    "get_total_count": true,
    "search_fields": {
      "name": "Acme"
    }
  }
}
```

**Query Parameters:**
- `row_count` - Number of records to return (default: 10, max: 100)
- `start_index` - Starting position for pagination (default: 1)
- `sort_field` - Field to sort by (e.g., "name", "created_time")
- `sort_order` - "asc" or "desc"
- `get_total_count` - Boolean to include total count
- `search_fields` - Object with field:value pairs for filtering

**Response Example:**
```json
{
  "response_status": {
    "status_code": 2000,
    "status": "success"
  },
  "list_info": {
    "has_more_rows": false,
    "row_count": 2,
    "start_index": 1,
    "total_count": 2
  },
  "accounts": [
    {
      "id": "12345",
      "name": "Acme Corporation",
      "website": "https://acme.com",
      "phone": "+1-555-0100",
      "account_type": {
        "name": "Customer",
        "id": "1"
      },
      "industry": {
        "name": "Technology",
        "id": "5"
      },
      "created_time": {
        "display_value": "Dec 18, 2025 10:30 AM",
        "value": "1734518400000"
      }
    }
  ]
}
```

---

### 2. Get Specific Account

**Endpoint:** `GET /accounts/{account_id}`

**Permission Required:** Technician or Admin

**Description:** Retrieve detailed information about a specific account.

**URL Parameters:**
- `account_id` - The unique ID of the account

**Response Example:**
```json
{
  "response_status": {
    "status_code": 2000,
    "status": "success"
  },
  "account": {
    "id": "12345",
    "name": "Acme Corporation",
    "website": "https://acme.com",
    "phone": "+1-555-0100",
    "fax": "+1-555-0101",
    "account_type": {
      "name": "Customer",
      "id": "1"
    },
    "industry": {
      "name": "Technology",
      "id": "5"
    },
    "address": {
      "street": "123 Main Street",
      "city": "San Francisco",
      "state": "California",
      "zip_code": "94105",
      "country": "USA"
    },
    "description": "Leading provider of innovative solutions",
    "created_time": {
      "display_value": "Dec 18, 2025 10:30 AM",
      "value": "1734518400000"
    },
    "updated_time": {
      "display_value": "Dec 18, 2025 02:15 PM",
      "value": "1734532500000"
    }
  }
}
```

---

### 3. Create New Account

**Endpoint:** `POST /accounts`

**Permission Required:** Admin

**Description:** Create a new account/organization.

**Request Example:**
```json
{
  "account": {
    "name": "New Company Inc",
    "website": "https://newcompany.com",
    "phone": "+1-555-0200",
    "fax": "+1-555-0201",
    "account_type": {
      "name": "Customer"
    },
    "industry": {
      "name": "Technology"
    },
    "address": {
      "street": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip_code": "02101",
      "country": "USA"
    },
    "description": "New customer account",
    "annual_revenue": "5000000",
    "number_of_employees": 150
  }
}
```

**Required Fields:**
- `name` - Account name (string)

**Optional Fields:**
- `website` - Company website (string)
- `phone` - Contact phone (string)
- `fax` - Fax number (string)
- `account_type` - Type of account (object with name or id)
- `industry` - Industry classification (object with name or id)
- `address` - Physical address (object)
- `description` - Account description (string)
- `annual_revenue` - Annual revenue (string)
- `number_of_employees` - Employee count (integer)

**Response Example:**
```json
{
  "response_status": {
    "status_code": 2000,
    "status": "success"
  },
  "account": {
    "id": "67890",
    "name": "New Company Inc",
    "website": "https://newcompany.com"
  }
}
```

---

### 4. Update Account

**Endpoint:** `PUT /accounts/{account_id}`

**Permission Required:** Admin

**Description:** Update an existing account's information.

**URL Parameters:**
- `account_id` - The unique ID of the account to update

**Request Example:**
```json
{
  "account": {
    "name": "Updated Company Name",
    "phone": "+1-555-9999",
    "website": "https://updatedcompany.com",
    "description": "Updated description"
  }
}
```

**Notes:**
- Only include fields you want to update
- Existing values for omitted fields will remain unchanged

**Response Example:**
```json
{
  "response_status": {
    "status_code": 2000,
    "status": "success"
  },
  "account": {
    "id": "12345",
    "name": "Updated Company Name",
    "phone": "+1-555-9999"
  }
}
```

---

### 5. Delete Account

**Endpoint:** `DELETE /accounts/{account_id}`

**Permission Required:** Admin

**Description:** Delete an account from the system.

**URL Parameters:**
- `account_id` - The unique ID of the account to delete

**Warning:** This operation cannot be undone. All associated data (contacts, sites) may also be affected.

**Response Example:**
```json
{
  "response_status": {
    "status_code": 2000,
    "status": "success",
    "messages": [
      {
        "status_code": 2000,
        "message": "Account deleted successfully"
      }
    ]
  }
}
```

---

### 6. Get Account Contacts

**Endpoint:** `GET /accounts/{account_id}/contacts`

**Permission Required:** Technician or Admin

**Description:** Retrieve all contacts associated with an account.

**URL Parameters:**
- `account_id` - The unique ID of the account

**Request Example:**
```json
{
  "list_info": {
    "row_count": 25,
    "start_index": 1
  }
}
```

**Response Example:**
```json
{
  "response_status": {
    "status_code": 2000,
    "status": "success"
  },
  "contacts": [
    {
      "id": "11111",
      "name": "John Doe",
      "email": "john.doe@acme.com",
      "phone": "+1-555-0150",
      "is_primary": true,
      "department": "IT"
    },
    {
      "id": "22222",
      "name": "Jane Smith",
      "email": "jane.smith@acme.com",
      "phone": "+1-555-0151",
      "is_primary": false,
      "department": "Operations"
    }
  ]
}
```

---

### 7. Get Account Sites

**Endpoint:** `GET /accounts/{account_id}/sites`

**Permission Required:** Technician or Admin

**Description:** Retrieve all sites/locations associated with an account.

**URL Parameters:**
- `account_id` - The unique ID of the account

**Request Example:**
```json
{
  "list_info": {
    "row_count": 25,
    "start_index": 1
  }
}
```

**Response Example:**
```json
{
  "response_status": {
    "status_code": 2000,
    "status": "success"
  },
  "sites": [
    {
      "id": "33333",
      "name": "Main Office",
      "address": {
        "street": "123 Main Street",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105"
      },
      "is_primary": true
    },
    {
      "id": "44444",
      "name": "Branch Office",
      "address": {
        "street": "789 Market Street",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90001"
      },
      "is_primary": false
    }
  ]
}
```

---

## Common Search Fields

When using `search_fields` in the list endpoint, you can filter by:

- `name` - Account name (partial match)
- `website` - Website URL (partial match)
- `phone` - Phone number (partial match)
- `account_type.name` - Account type name
- `industry.name` - Industry name
- `created_time` - Creation timestamp
- `updated_time` - Last update timestamp

**Example:**
```json
{
  "list_info": {
    "search_fields": {
      "name": "Corporation",
      "account_type.name": "Customer",
      "industry.name": "Technology"
    }
  }
}
```

---

## Error Codes

| Status Code | Meaning |
|-------------|---------|
| 2000 | Success |
| 4000 | Bad request (invalid input) |
| 4001 | Authentication failed |
| 4003 | Permission denied |
| 4004 | Account not found |
| 4103 | Duplicate account name |
| 5000 | Internal server error |

---

## Best Practices

### 1. **Pagination**
Always use pagination for large datasets:
```json
{
  "list_info": {
    "row_count": 25,
    "start_index": 1
  }
}
```

### 2. **Field Selection**
Request only the fields you need to reduce response size.

### 3. **Error Handling**
Always check `response_status.status_code` before processing results.

### 4. **Rate Limiting**
Be mindful of API rate limits. Implement exponential backoff for retries.

### 5. **Validation**
Validate account data before creation/update:
- Account name is required and unique
- Email/website format validation
- Phone number format consistency

---

## Usage in SDP Explorer

### Via Web Interface

1. **Login** to SDP Explorer at `http://127.0.0.1:5000`
2. **Navigate** to the API Explorer page
3. **Select** "Accounts" from the category dropdown
4. **Choose** an endpoint (list, view, add, update, etc.)
5. **Fill in** placeholders (e.g., `account_id`)
6. **Enter** input_data as JSON
7. **Click** "Execute"

### Via Saved Queries

1. Create a query with common account searches
2. Save as "Get Active Customers" or similar
3. Mark as favorite for quick access
4. Reuse with one click

### Via Bulk Operations

For bulk account updates:
1. Use the Bulk Operations tool (coming soon)
2. Filter accounts by criteria
3. Apply changes to multiple accounts
4. Review and confirm changes

---

## Integration Examples

### Example 1: Sync Accounts from CRM

```python
# Fetch accounts from external CRM
crm_accounts = fetch_from_crm()

# Create/update in SDP
for crm_account in crm_accounts:
    sdp_account = {
        "account": {
            "name": crm_account['company_name'],
            "website": crm_account['website'],
            "phone": crm_account['phone'],
            "industry": {"name": crm_account['industry']}
        }
    }

    # Create in SDP
    result = api_call('POST', '/accounts', data=sdp_account)
```

### Example 2: Generate Account Report

```python
# Fetch all accounts
all_accounts = []
start_index = 1

while True:
    result = api_call('GET', '/accounts', data={
        'list_info': {
            'row_count': 100,
            'start_index': start_index
        }
    })

    all_accounts.extend(result['accounts'])

    if not result['list_info']['has_more_rows']:
        break

    start_index += 100

# Generate report
generate_csv_report(all_accounts)
```

### Example 3: Account Health Check

```python
# Find accounts with missing data
accounts = api_call('GET', '/accounts', data={
    'list_info': {'row_count': 100}
})

incomplete_accounts = []
for account in accounts['accounts']:
    if not account.get('phone') or not account.get('website'):
        incomplete_accounts.append(account)

# Alert or export for cleanup
send_alert(f"{len(incomplete_accounts)} accounts need updating")
```

---

## Testing

Run the test script to verify endpoints:

```bash
python test_accounts_api.py
```

This will test all accounts endpoints and show example requests/responses.

---

## Related APIs

- **Contacts API**: Manage individual contacts within accounts
- **Sites API**: Manage physical locations for accounts
- **Requests API**: View tickets associated with accounts
- **Assets API**: Track assets owned by accounts

---

## Troubleshooting

### Issue: "Permission Denied"
**Solution:** Ensure your API key has Admin privileges for write operations.

### Issue: "Account Not Found"
**Solution:** Verify the account_id exists and is accessible to your user.

### Issue: "Duplicate Account Name"
**Solution:** Account names must be unique. Check if account already exists.

### Issue: Empty Response
**Solution:** Check filters in search_fields. Try without filters first.

---

## Support

For ME SDP API issues:
- Check ManageEngine API documentation
- Contact your SDP administrator
- Review API logs in request history

For SDP Explorer issues:
- Check application logs
- Review request history for errors
- Test endpoints with test script first
