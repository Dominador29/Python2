"""
Project Activity 4 - THE DREAM TEAM
Members: Jade Lloyd de Lara, Carlos Alfonso Perez, Maverick Angelo Sibal, John Rafael Villacorte

Version: 2.0.0
Team: THE DREAM TEAM
Date: November 30, 2025
"""

from flask import Flask, jsonify, request
import requests
from datetime import datetime
import time

app = Flask(__name__)

__version__ = "2.0.0"
__team__ = "THE DREAM TEAM"

# In-memory storage for IP lookup history
ip_history = []

class IPInfoError(Exception):
    """Custom exception for IP information errors"""
    pass

def fetch_ipv4():
    """
    Fetch public IPv4 address
    Returns: IPv4 address string
    Raises: IPInfoError if unable to fetch
    """
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            return response.json()['ip']
        raise IPInfoError(f"Failed to fetch IPv4: Status {response.status_code}")
    except requests.exceptions.Timeout:
        raise IPInfoError("Request timeout while fetching IPv4")
    except requests.exceptions.ConnectionError:
        raise IPInfoError("Connection error while fetching IPv4")
    except Exception as e:
        raise IPInfoError(f"Error fetching IPv4: {str(e)}")

def fetch_ipv6():
    """
    Fetch public IPv6 address if available
    Returns: IPv6 address string or None
    """
    try:
        response = requests.get('https://api64.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            ipv6 = response.json()['ip']
            return ipv6 if ':' in ipv6 else None
        return None
    except:
        return None

def fetch_ip_details(ip_address):
    """
    Fetch detailed information for an IP address
    Args: ip_address - IP to lookup
    Returns: Dictionary with IP details
    Raises: IPInfoError if unable to fetch
    """
    try:
        fields = "status,message,continent,continentCode,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,query"
        url = f"http://ip-api.com/json/{ip_address}?fields={fields}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data
            else:
                raise IPInfoError(data.get('message', 'Unknown API error'))
        elif response.status_code == 429:
            raise IPInfoError("API rate limit reached")
        else:
            raise IPInfoError(f"HTTP error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        raise IPInfoError("Request timeout")
    except requests.exceptions.ConnectionError:
        raise IPInfoError("Connection failed")
    except IPInfoError:
        raise
    except Exception as e:
        raise IPInfoError(f"Error: {str(e)}")

@app.route('/')
def home():
    """API home endpoint with documentation"""
    return jsonify({
        'application': 'IP Address Information API',
        'version': __version__,
        'team': __team__,
        'endpoints': {
            'GET /': 'API documentation',
            'GET /api/myip': 'Get your IP information',
            'GET /api/lookup/<ip>': 'Lookup specific IP address',
            'GET /api/history': 'Get lookup history',
            'DELETE /api/history': 'Clear lookup history',
            'GET /api/stats': 'Get API statistics',
            'GET /health': 'Health check'
        }
    })

@app.route('/api/myip', methods=['GET'])
def get_my_ip():
    """
    Get current user's IP information
    Returns: JSON with IPv4, IPv6 (if available), and geolocation data
    """
    try:
        ipv4 = fetch_ipv4()
        ipv6 = fetch_ipv6()
        
        time.sleep(0.5)  # Rate limiting courtesy
        
        details = fetch_ip_details(ipv4)
        
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': {
                'ipv4': ipv4,
                'ipv6': ipv6 if ipv6 else 'Not Available',
                'location': {
                    'city': details.get('city', 'N/A'),
                    'region': details.get('regionName', 'N/A'),
                    'country': details.get('country', 'N/A'),
                    'country_code': details.get('countryCode', 'N/A'),
                    'continent': details.get('continent', 'N/A'),
                    'postal_code': details.get('zip', 'N/A'),
                    'coordinates': {
                        'latitude': details.get('lat', 0),
                        'longitude': details.get('lon', 0)
                    },
                    'timezone': details.get('timezone', 'N/A')
                },
                'network': {
                    'isp': details.get('isp', 'N/A'),
                    'organization': details.get('org', 'N/A'),
                    'as': details.get('as', 'N/A'),
                    'asn_name': details.get('asname', 'N/A')
                }
            }
        }
        
        # Add to history
        ip_history.append({
            'ip': ipv4,
            'timestamp': result['timestamp'],
            'city': details.get('city', 'N/A'),
            'country': details.get('country', 'N/A')
        })
        
        return jsonify(result), 200
        
    except IPInfoError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/lookup/<ip_address>', methods=['GET'])
def lookup_ip(ip_address):
    """
    Lookup information for a specific IP address
    Args: ip_address - IP to lookup (URL parameter)
    Returns: JSON with IP information
    """
    try:
        # Basic IP validation
        if not ip_address or ip_address == '':
            return jsonify({
                'success': False,
                'error': 'IP address is required'
            }), 400
        
        details = fetch_ip_details(ip_address)
        
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'query': ip_address,
            'data': {
                'location': {
                    'city': details.get('city', 'N/A'),
                    'region': details.get('regionName', 'N/A'),
                    'country': details.get('country', 'N/A'),
                    'country_code': details.get('countryCode', 'N/A'),
                    'postal_code': details.get('zip', 'N/A'),
                    'coordinates': {
                        'latitude': details.get('lat', 0),
                        'longitude': details.get('lon', 0)
                    },
                    'timezone': details.get('timezone', 'N/A')
                },
                'network': {
                    'isp': details.get('isp', 'N/A'),
                    'organization': details.get('org', 'N/A'),
                    'as': details.get('as', 'N/A'),
                    'asn_name': details.get('asname', 'N/A')
                }
            }
        }
        
        # Add to history
        ip_history.append({
            'ip': ip_address,
            'timestamp': result['timestamp'],
            'city': details.get('city', 'N/A'),
            'country': details.get('country', 'N/A')
        })
        
        return jsonify(result), 200
        
    except IPInfoError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Get IP lookup history
    Returns: JSON array of previous lookups
    """
    limit = request.args.get('limit', default=10, type=int)
    
    if limit < 1 or limit > 100:
        return jsonify({
            'success': False,
            'error': 'Limit must be between 1 and 100'
        }), 400
    
    return jsonify({
        'success': True,
        'count': len(ip_history),
        'limit': limit,
        'history': ip_history[-limit:]
    }), 200

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """
    Clear IP lookup history
    Returns: Success message
    """
    global ip_history
    count = len(ip_history)
    ip_history = []
    
    return jsonify({
        'success': True,
        'message': f'Cleared {count} history entries'
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get API usage statistics
    Returns: JSON with statistics
    """
    unique_ips = len(set(item['ip'] for item in ip_history))
    countries = {}
    
    for item in ip_history:
        country = item.get('country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1
    
    return jsonify({
        'success': True,
        'statistics': {
            'total_lookups': len(ip_history),
            'unique_ips': unique_ips,
            'countries_accessed': len(countries),
            'top_countries': sorted(
                countries.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    Returns: Service health status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'IP Info API',
        'version': __version__,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'Please check API documentation at /'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)