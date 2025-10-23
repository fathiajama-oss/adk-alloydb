from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace with your actual API key
GOOGLE_MAPS_API_KEY = "AIzaSyBcR__DWZACouW-ACPSeNdGEFI8LMlt4sw"

def geocode_address(address):
    """
    Convert an address to latitude and longitude using Google Geocoding API
    Returns: (latitude, longitude) tuple or (None, None) if failed
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': GOOGLE_MAPS_API_KEY
    }
    
    try:
        print(f"Geocoding address: {address}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'OK' and data.get('results'):
            location = data['results'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            print(f"✓ Geocoded to: {lat}, {lng}")
            return lat, lng
        else:
            print(f"✗ Geocoding failed: {data.get('status')}")
            return None, None
            
    except Exception as e:
        print(f"✗ Geocoding error: {str(e)}")
        return None, None

@app.route('/nearby-search', methods=['GET'])
def nearby_search():
    """
    Proxy for Google Places Nearby Search API
    Query params: 
      - query: provider type (e.g., 'dentist')
      - address: street address to search near (e.g., '123 Main St, Anytown, CA')
      OR
      - latitude & longitude: coordinates to search near
      - radius: search radius in meters (optional, default 50000)
    """
    query = request.args.get('query', 'dentist')
    address = request.args.get('address')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    radius = request.args.get('radius', '50000')
    
    # If address is provided, geocode it to get coordinates
    if address:
        print(f"\n{'='*60}")
        print(f"Request: Find '{query}' near address '{address}'")
        print(f"{'='*60}")
        
        lat, lng = geocode_address(address)
        
        if lat is None or lng is None:
            return jsonify({
                'error': 'Failed to geocode address',
                'address': address
            }), 400
        
        latitude = str(lat)
        longitude = str(lng)
    else:
        # Use provided coordinates or defaults
        latitude = latitude or '37.7749'
        longitude = longitude or '-122.4194'
        print(f"\n{'='*60}")
        print(f"Request: Find '{query}' near coordinates {latitude},{longitude}")
        print(f"{'='*60}")
    
    print(f"Searching within {radius}m radius...")
    
    # Call Places API
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,
        'keyword': query,
        'type': 'health',
        'key': GOOGLE_MAPS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Simplify response
        results = []
        if data.get('results'):
            for place in data['results'][:5]:
                results.append({
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'latitude': place.get('geometry', {}).get('location', {}).get('lat'),
                    'longitude': place.get('geometry', {}).get('location', {}).get('lng'),
                    'rating': place.get('rating'),
                    'open_now': place.get('opening_hours', {}).get('open_now')
                })
        
        print(f"✓ Found {len(results)} providers")
        print(f"{'='*60}\n")
        
        return jsonify({
            'status': data.get('status'),
            'count': len(results),
            'search_location': {
                'latitude': latitude,
                'longitude': longitude,
                'address': address if address else None
            },
            'results': results
        })
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/geocode', methods=['GET'])
def geocode():
    """
    Standalone geocoding endpoint for testing
    Query param: address
    """
    address = request.args.get('address')
    
    if not address:
        return jsonify({'error': 'Address parameter required'}), 400
    
    lat, lng = geocode_address(address)
    
    if lat is None or lng is None:
        return jsonify({
            'error': 'Failed to geocode address',
            'address': address
        }), 400
    
    return jsonify({
        'address': address,
        'latitude': lat,
        'longitude': lng
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Places API Proxy with Geocoding',
        'geocoding_enabled': True
    })

if __name__ == '__main__':
    print("🚀 Starting Places API Proxy with Geocoding on http://localhost:8080")
    print(f"API Key configured: {'Yes' if GOOGLE_MAPS_API_KEY != 'YOUR_API_KEY_HERE' else 'No - UPDATE ME!'}")
    print("\nEndpoints:")
    print("  GET /nearby-search?query=dentist&address=123 Main St, Anytown")
    print("  GET /nearby-search?query=dentist&latitude=37.7749&longitude=-122.4194")
    print("  GET /geocode?address=123 Main St, Anytown")
    print("  GET /health")
    print()
    app.run(host='0.0.0.0', port=8080, debug=True)
