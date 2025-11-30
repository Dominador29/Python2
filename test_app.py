"""
Test Suite for IP Address Information API
THE DREAM TEAM
"""

import pytest
import json
from unittest.mock import patch, Mock
from app import app, ip_history, IPInfoError

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    ip_history.clear()

@pytest.fixture
def mock_ip_details():
    return {
        'status': 'success',
        'city': 'Mountain View',
        'regionName': 'California',
        'country': 'United States',
        'countryCode': 'US',
        'continent': 'North America',
        'zip': '94035',
        'lat': 37.386,
        'lon': -122.0838,
        'timezone': 'America/Los_Angeles',
        'isp': 'Google LLC',
        'org': 'Google Public DNS',
        'as': 'AS15169 Google LLC',
        'asname': 'GOOGLE',
        'query': '8.8.8.8'
    }

def test_home_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'application' in data
    assert data['team'] == 'THE DREAM TEAM'

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

@patch('app.fetch_ipv4')
@patch('app.fetch_ip_details')
def test_get_my_ip_success(mock_details, mock_ipv4, client):
    mock_ipv4.return_value = '8.8.8.8'
    mock_details.return_value = {
        'city': 'Mountain View',
        'regionName': 'California',
        'country': 'United States',
        'countryCode': 'US',
        'continent': 'North America',
        'zip': '94035',
        'lat': 37.386,
        'lon': -122.0838,
        'timezone': 'America/Los_Angeles',
        'isp': 'Google LLC',
        'org': 'Google Public DNS',
        'as': 'AS15169 Google LLC',
        'asname': 'GOOGLE'
    }
    
    response = client.get('/api/myip')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

@patch('app.fetch_ip_details')
def test_lookup_ip_success(mock_details, client, mock_ip_details):
    mock_details.return_value = mock_ip_details
    
    response = client.get('/api/lookup/8.8.8.8')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_get_history_empty(client):
    response = client.get('/api/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 0

def test_get_stats_empty(client):
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['statistics']['total_lookups'] == 0