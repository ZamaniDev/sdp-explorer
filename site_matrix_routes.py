"""
Routes for Technician-Site Matrix Manager
Allows admins to visually manage technician-site associations
"""
from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from app import app
from decorators import requires_permission, get_appropriate_credential
import requests
import json
from datetime import datetime


def api_call_with_credential(credential, method, endpoint, params=None, data=None):
    """Make API call using specific credential"""
    url = f"{credential.api_base_url}{endpoint}"
    headers = {"authtoken": credential.api_key}

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, verify=False)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, data=data, verify=False)

        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json() if response.text else {},
            "raw": response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.route('/tools/site-matrix')
@login_required
def site_matrix():
    """Technician-Site Matrix Manager page"""
    return render_template('site_matrix.html')


@app.route('/api/tools/site-matrix/data', methods=['GET'])
@login_required
def get_site_matrix_data():
    """
    Get all technicians and sites for matrix display
    Returns both lists to build the matrix
    """
    # Get admin credential (required for reading all technicians)
    admin_cred = get_appropriate_credential(current_user, 'admin')
    if not admin_cred:
        # Try technician credential as fallback
        admin_cred = get_appropriate_credential(current_user, 'technician')

    if not admin_cred:
        return jsonify({
            'success': False,
            'error': 'No API credential configured. Please add credentials in your profile.'
        }), 403

    # Fetch all technicians
    techs_response = api_call_with_credential(
        admin_cred,
        'GET',
        '/technicians',
        params={
            'input_data': json.dumps({
                "list_info": {
                    "row_count": 100,
                    "start_index": 1
                }
            })
        }
    )

    if not techs_response['success']:
        return jsonify({
            'success': False,
            'error': f"Failed to fetch technicians: {techs_response.get('error')}"
        }), 500

    # Fetch all sites/accounts
    sites_response = api_call_with_credential(
        admin_cred,
        'GET',
        '/sites',
        params={
            'input_data': json.dumps({
                "list_info": {
                    "row_count": 100,
                    "start_index": 1
                }
            })
        }
    )

    # If sites endpoint doesn't exist, try accounts
    if not sites_response['success'] or not sites_response['data'].get('sites'):
        sites_response = api_call_with_credential(
            admin_cred,
            'GET',
            '/accounts',
            params={
                'input_data': json.dumps({
                    "list_info": {
                        "row_count": 100,
                        "start_index": 1
                    }
                })
            }
        )

    technicians_data = techs_response['data'].get('technicians', [])
    sites_data = sites_response['data'].get('sites', sites_response['data'].get('accounts', []))

    # Build simplified data structure
    technicians = []
    for tech in technicians_data:
        associated_site_ids = [site['id'] for site in tech.get('associated_sites', [])]

        technicians.append({
            'id': tech['id'],
            'name': tech.get('name', 'Unknown'),
            'email': tech.get('email_id', ''),
            'status': tech.get('status', 'ACTIVE'),
            'department': tech.get('department', {}).get('name', ''),
            'associated_sites': tech.get('associated_sites', []),
            'associated_site_ids': associated_site_ids
        })

    sites = []
    for site in sites_data:
        sites.append({
            'id': site['id'],
            'name': site.get('name', 'Unknown'),
            'account': site.get('account', {}).get('name', '') if 'account' in site else ''
        })

    return jsonify({
        'success': True,
        'technicians': technicians,
        'sites': sites,
        'total_technicians': len(technicians),
        'total_sites': len(sites)
    })


@app.route('/api/tools/site-matrix/technician/<int:tech_id>', methods=['GET'])
@login_required
def get_technician_details(tech_id):
    """Get detailed technician info including current associated sites"""
    admin_cred = get_appropriate_credential(current_user, 'admin')
    if not admin_cred:
        admin_cred = get_appropriate_credential(current_user, 'technician')

    if not admin_cred:
        return jsonify({
            'success': False,
            'error': 'No API credential configured'
        }), 403

    response = api_call_with_credential(
        admin_cred,
        'GET',
        f'/technicians/{tech_id}'
    )

    if not response['success']:
        return jsonify(response), 500

    technician = response['data'].get('technician', {})

    return jsonify({
        'success': True,
        'technician': {
            'id': technician['id'],
            'name': technician.get('name', 'Unknown'),
            'email': technician.get('email_id', ''),
            'associated_sites': technician.get('associated_sites', [])
        }
    })


@app.route('/api/tools/site-matrix/update', methods=['PUT'])
@login_required
def update_technician_sites():
    """
    Update technician's associated sites
    Requires admin credential
    """
    data = request.json
    tech_id = data.get('technician_id')
    new_site_ids = data.get('site_ids', [])

    if not tech_id:
        return jsonify({
            'success': False,
            'error': 'Technician ID is required'
        }), 400

    # Get admin credential (required for updates)
    admin_cred = get_appropriate_credential(current_user, 'admin')
    if not admin_cred:
        return jsonify({
            'success': False,
            'error': 'Admin API credential required for updating technicians'
        }), 403

    # Build associated_sites array from IDs
    associated_sites = [{"id": str(site_id)} for site_id in new_site_ids]

    # Prepare update payload
    update_data = {
        "technician": {
            "associated_sites": associated_sites
        }
    }

    # Make PUT request
    response = api_call_with_credential(
        admin_cred,
        'PUT',
        f'/technicians/{tech_id}',
        data={'input_data': json.dumps(update_data)}
    )

    if response['success']:
        return jsonify({
            'success': True,
            'message': f"Updated technician {tech_id} successfully",
            'technician_id': tech_id,
            'site_count': len(new_site_ids)
        })
    else:
        return jsonify({
            'success': False,
            'error': response.get('error', 'Unknown error'),
            'response': response.get('data')
        }), 500


@app.route('/api/tools/site-matrix/bulk-update', methods=['PUT'])
@login_required
def bulk_update_technician_sites():
    """
    Bulk update multiple technicians' sites
    """
    data = request.json
    updates = data.get('updates', [])  # [{technician_id: 123, site_ids: [1,2,3]}, ...]

    if not updates:
        return jsonify({
            'success': False,
            'error': 'No updates provided'
        }), 400

    admin_cred = get_appropriate_credential(current_user, 'admin')
    if not admin_cred:
        return jsonify({
            'success': False,
            'error': 'Admin API credential required'
        }), 403

    results = {
        'success': [],
        'failed': [],
        'total': len(updates)
    }

    for update in updates:
        tech_id = update.get('technician_id')
        site_ids = update.get('site_ids', [])

        associated_sites = [{"id": str(site_id)} for site_id in site_ids]
        update_data = {
            "technician": {
                "associated_sites": associated_sites
            }
        }

        response = api_call_with_credential(
            admin_cred,
            'PUT',
            f'/technicians/{tech_id}',
            data={'input_data': json.dumps(update_data)}
        )

        if response['success']:
            results['success'].append({
                'technician_id': tech_id,
                'site_count': len(site_ids)
            })
        else:
            results['failed'].append({
                'technician_id': tech_id,
                'error': response.get('error', 'Unknown error')
            })

    return jsonify({
        'success': True,
        'results': results
    })
