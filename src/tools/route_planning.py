"""
Route Planning and Weather Analysis Tool
Analyzes weather conditions along a route between cities
"""

from typing import List, Dict, Any, Optional, Tuple
import math
import os
import requests
import structlog
from datetime import datetime
from google.genai import Client

from .custom_tools import geocode_location, get_weather_data

logger = structlog.get_logger()


def verify_route_with_ai(start_city: str, end_city: str, cities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Use Gemini AI to verify and filter the route cities to only major ones.
    
    Args:
        start_city: Starting city
        end_city: Ending city
        cities: List of cities found on route
        
    Returns:
        Filtered list of only major cities
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("route.ai_verify.no_api_key")
            return cities  # Return as-is if no AI available
        
        client = Client(api_key=api_key)
        
        # Prepare city list for AI
        city_list = [f"{c['name']} ({c['distance_from_start']} km)" for c in cities]
        
        prompt = f"""You are a route planning expert for India. 
        
Route: {start_city} to {end_city}
Cities found: {', '.join(city_list)}

Task: Filter this list to show ONLY major cities (population > 100,000 or district headquarters). 
Remove small towns, suburbs, and neighborhoods.

For Chennai to Trichy route, major cities would be: Chennai, Chengalpattu, Tindivanam, Villupuram, Cuddalore, Chidambaram, Kumbakonam, Trichy
For Chennai to Nagapattinam: Chennai, Mahabalipuram, Puducherry, Cuddalore, Chidambaram, Mayiladuthurai, Nagapattinam

Return ONLY the city names that are major cities, one per line, no explanations.
If a city appears in the list, include it. Keep 5-8 major cities maximum.
"""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        # Parse AI response
        ai_cities = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        
        # Filter original cities to match AI selection
        filtered = []
        for city in cities:
            # Check if AI selected this city (case-insensitive)
            if any(ai_city.lower() in city['name'].lower() or city['name'].lower() in ai_city.lower() 
                   for ai_city in ai_cities):
                filtered.append(city)
        
        logger.info("route.ai_verify.success", 
                   original_count=len(cities),
                   filtered_count=len(filtered),
                   ai_selected=ai_cities)
        
        return filtered if filtered else cities[:6]  # Fallback to first 6 if AI filter fails
        
    except Exception as e:
        logger.error("route.ai_verify.error", error=str(e))
        return cities  # Return original on error


# Major cities database for India (can be extended)
# This is used as a fallback and for known major cities
MAJOR_CITIES_INDIA = {
    # Tamil Nadu - Chennai and surrounding areas
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu"},
    "Adyar": {"lat": 13.0067, "lon": 80.2572, "state": "Tamil Nadu"},
    "Ambattur": {"lat": 13.0987, "lon": 80.1610, "state": "Tamil Nadu"},
    "Anna Nagar": {"lat": 13.0850, "lon": 80.2101, "state": "Tamil Nadu"},
    "Avadi": {"lat": 13.1147, "lon": 80.1018, "state": "Tamil Nadu"},
    "Egmore": {"lat": 13.0732, "lon": 80.2609, "state": "Tamil Nadu"},
    "Guindy": {"lat": 13.0067, "lon": 80.2206, "state": "Tamil Nadu"},
    "Kodambakkam": {"lat": 13.0524, "lon": 80.2270, "state": "Tamil Nadu"},
    "Mylapore": {"lat": 13.0339, "lon": 80.2619, "state": "Tamil Nadu"},
    "Nungambakkam": {"lat": 13.0594, "lon": 80.2428, "state": "Tamil Nadu"},
    "Perambur": {"lat": 13.1105, "lon": 80.2326, "state": "Tamil Nadu"},
    "Porur": {"lat": 13.0358, "lon": 80.1568, "state": "Tamil Nadu"},
    "T Nagar": {"lat": 13.0418, "lon": 80.2341, "state": "Tamil Nadu"},
    "Tambaram": {"lat": 12.9249, "lon": 80.1000, "state": "Tamil Nadu"},
    "Velachery": {"lat": 12.9750, "lon": 80.2210, "state": "Tamil Nadu"},
    
    # Tamil Nadu - Coastal Cities (Chennai to Nagapattinam route)
    "Chengalpattu": {"lat": 12.6947, "lon": 79.9837, "state": "Tamil Nadu"},
    "Mahabalipuram": {"lat": 12.6208, "lon": 80.1989, "state": "Tamil Nadu"},
    "Puducherry": {"lat": 11.9139, "lon": 79.8145, "state": "Puducherry"},
    "Cuddalore": {"lat": 11.7480, "lon": 79.7714, "state": "Tamil Nadu"},
    "Chidambaram": {"lat": 11.3991, "lon": 79.6914, "state": "Tamil Nadu"},
    "Mayiladuthurai": {"lat": 11.1028, "lon": 79.6556, "state": "Tamil Nadu"},
    "Nagapattinam": {"lat": 10.7660, "lon": 79.8419, "state": "Tamil Nadu"},
    "Karaikal": {"lat": 10.9254, "lon": 79.8380, "state": "Puducherry"},
    "Thiruvarur": {"lat": 10.7724, "lon": 79.6345, "state": "Tamil Nadu"},
    
    # Tamil Nadu - Other Major Cities
    "Trichy": {"lat": 10.7905, "lon": 78.7047, "state": "Tamil Nadu"},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047, "state": "Tamil Nadu"},
    "Thanjavur": {"lat": 10.7870, "lon": 79.1378, "state": "Tamil Nadu"},
    "Villupuram": {"lat": 11.9401, "lon": 79.4861, "state": "Tamil Nadu"},
    "Perambalur": {"lat": 11.2324, "lon": 78.8798, "state": "Tamil Nadu"},
    "Ariyalur": {"lat": 11.1401, "lon": 79.0766, "state": "Tamil Nadu"},
    "Salem": {"lat": 11.6643, "lon": 78.1460, "state": "Tamil Nadu"},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558, "state": "Tamil Nadu"},
    "Madurai": {"lat": 9.9252, "lon": 78.1198, "state": "Tamil Nadu"},
    "Vellore": {"lat": 12.9165, "lon": 79.1325, "state": "Tamil Nadu"},
    "Kanchipuram": {"lat": 12.8342, "lon": 79.7036, "state": "Tamil Nadu"},
    "Hosur": {"lat": 12.7409, "lon": 77.8253, "state": "Tamil Nadu"},
    "Krishnagiri": {"lat": 12.5186, "lon": 78.2137, "state": "Tamil Nadu"},
    "Dharmapuri": {"lat": 12.1211, "lon": 78.1582, "state": "Tamil Nadu"},
    "Tindivanam": {"lat": 12.2333, "lon": 79.6500, "state": "Tamil Nadu"},
    
    # Maharashtra - Mumbai and surrounding areas
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra"},
    "Andheri": {"lat": 19.1136, "lon": 72.8697, "state": "Maharashtra"},
    "Bandra": {"lat": 19.0596, "lon": 72.8295, "state": "Maharashtra"},
    "Borivali": {"lat": 19.2403, "lon": 72.8540, "state": "Maharashtra"},
    "Churchgate": {"lat": 18.9322, "lon": 72.8264, "state": "Maharashtra"},
    "Dadar": {"lat": 19.0176, "lon": 72.8481, "state": "Maharashtra"},
    "Goregaon": {"lat": 19.1653, "lon": 72.8489, "state": "Maharashtra"},
    "Juhu": {"lat": 19.0990, "lon": 72.8266, "state": "Maharashtra"},
    "Kandivali": {"lat": 19.2074, "lon": 72.8537, "state": "Maharashtra"},
    "Kurla": {"lat": 19.0658, "lon": 72.8789, "state": "Maharashtra"},
    "Malad": {"lat": 19.1859, "lon": 72.8488, "state": "Maharashtra"},
    "Navi Mumbai": {"lat": 19.0330, "lon": 73.0297, "state": "Maharashtra"},
    "Powai": {"lat": 19.1176, "lon": 72.9060, "state": "Maharashtra"},
    "Thane": {"lat": 19.2183, "lon": 72.9781, "state": "Maharashtra"},
    "Vashi": {"lat": 19.0770, "lon": 73.0169, "state": "Maharashtra"},
    "Worli": {"lat": 19.0176, "lon": 72.8170, "state": "Maharashtra"},
    
    # Maharashtra - Pune and surrounding areas
    "Pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    "Hinjewadi": {"lat": 18.5912, "lon": 73.7389, "state": "Maharashtra"},
    "Kothrud": {"lat": 18.5074, "lon": 73.8077, "state": "Maharashtra"},
    "Wakad": {"lat": 18.5978, "lon": 73.7643, "state": "Maharashtra"},
    "Pimpri-Chinchwad": {"lat": 18.6298, "lon": 73.7997, "state": "Maharashtra"},
    
    # Maharashtra - Other Major Cities
    "Nagpur": {"lat": 21.1458, "lon": 79.0882, "state": "Maharashtra"},
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "state": "Maharashtra"},
    "Aurangabad": {"lat": 19.8762, "lon": 75.3433, "state": "Maharashtra"},
    "Solapur": {"lat": 17.6599, "lon": 75.9064, "state": "Maharashtra"},
    
    # Karnataka
    "Bangalore": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
    
    # Telangana
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana"},
    
    # Delhi
    "Delhi": {"lat": 28.7041, "lon": 77.1025, "state": "Delhi"},
    "New Delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi"},
    
    # West Bengal
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "state": "West Bengal"},
    
    # Gujarat
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "state": "Gujarat"},
    "Surat": {"lat": 21.1702, "lon": 72.8311, "state": "Gujarat"},
}


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance


def is_point_near_route(
    point_lat: float, 
    point_lon: float,
    start_lat: float, 
    start_lon: float,
    end_lat: float, 
    end_lon: float,
    threshold_km: float = 50
) -> bool:
    """
    Check if a point is near the route between start and end.
    Uses perpendicular distance from line.
    
    Args:
        point_lat, point_lon: Point to check
        start_lat, start_lon: Route start
        end_lat, end_lon: Route end
        threshold_km: Maximum distance from route in km
        
    Returns:
        True if point is near the route
    """
    # Distance from point to start
    dist_to_start = calculate_distance(point_lat, point_lon, start_lat, start_lon)
    
    # Distance from point to end
    dist_to_end = calculate_distance(point_lat, point_lon, end_lat, end_lon)
    
    # Distance from start to end (route length)
    route_length = calculate_distance(start_lat, start_lon, end_lat, end_lon)
    
    # If point is very close to start or end, include it
    if dist_to_start < threshold_km or dist_to_end < threshold_km:
        return True
    
    # Check if point is roughly on the path
    # A point is on the route if: dist_to_start + dist_to_end ≈ route_length
    total_detour = dist_to_start + dist_to_end - route_length
    
    return total_detour < threshold_km


def get_route_from_google_maps(start_city: str, end_city: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get actual driving route waypoints using Google Maps Directions API.
    
    Args:
        start_city: Starting city name
        end_city: Ending city name
        
    Returns:
        List of waypoints with lat/lon along the route, or None if API fails
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        logger.warning("google_maps.no_api_key", 
                      message="Google Maps API key not configured. Set GOOGLE_MAPS_API_KEY in .env file for accurate routing.")
        return None
    
    try:
        # Add country qualifier for better accuracy
        origin = f"{start_city}, India"
        destination = f"{end_city}, India"
        
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "driving",
            "region": "IN",  # Prefer Indian routes
            "key": api_key
        }
        
        logger.info("google_maps.requesting_route", 
                   start=start_city, 
                   end=end_city,
                   origin=origin,
                   destination=destination)
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "OK" and data.get("routes"):
                route = data["routes"][0]
                legs = route.get("legs", [])
                
                # Log route summary
                if legs:
                    leg = legs[0]
                    distance = leg.get("distance", {}).get("text", "Unknown")
                    duration = leg.get("duration", {}).get("text", "Unknown")
                    start_addr = leg.get("start_address", start_city)
                    end_addr = leg.get("end_address", end_city)
                    
                    logger.info("google_maps.route_summary",
                               start_address=start_addr,
                               end_address=end_addr,
                               distance=distance,
                               duration=duration)
                
                waypoints = []
                for leg in legs:
                    steps = leg.get("steps", [])
                    for step in steps:
                        start_location = step.get("start_location", {})
                        waypoints.append({
                            "lat": start_location.get("lat"),
                            "lon": start_location.get("lng")
                        })
                
                logger.info("google_maps.route_found", 
                           start=start_city, 
                           end=end_city, 
                           waypoints=len(waypoints))
                return waypoints
            else:
                status = data.get("status")
                error_msg = data.get("error_message", "No route found")
                logger.warning("google_maps.no_route", 
                             start=start_city,
                             end=end_city,
                             status=status, 
                             error=error_msg)
                
                # Log available routes if status is ZERO_RESULTS
                if status == "ZERO_RESULTS":
                    logger.info("google_maps.zero_results_detail",
                               message=f"No route found between {origin} and {destination}. Check city names.")
        else:
            logger.error("google_maps.api_error", 
                        start=start_city,
                        end=end_city,
                        status=response.status_code,
                        response=response.text[:500])
            
    except Exception as e:
        logger.error("google_maps.exception", 
                    start=start_city,
                    end=end_city,
                    error=str(e))
    
    return None


def find_cities_from_route_waypoints(
    waypoints: List[Dict[str, Any]], 
    start_city: str,
    end_city: str,
    sample_interval: int = 5  # Back to 5 for better coverage
) -> List[Dict[str, Any]]:
    """
    Find cities along the route by sampling waypoints and reverse geocoding.
    Uses strategic sampling to capture important cities along the route.
    
    Args:
        waypoints: List of lat/lon waypoints from route
        start_city: Starting city name
        end_city: Ending city name
        sample_interval: Sample every Nth waypoint (default: 5 for good coverage)
        
    Returns:
        List of unique cities along the route
    """
    cities = []
    seen_cities = set()
    
    # Strategic sampling: first, quarter points, middle, three-quarter, last
    # This ensures we catch major junction cities
    total = len(waypoints)
    key_indices = [
        0,                    # Start
        total // 5,          # 20% point
        2 * total // 5,      # 40% point
        3 * total // 5,      # 60% point
        4 * total // 5,      # 80% point
        total - 1            # End
    ]
    regular_indices = list(range(0, len(waypoints), sample_interval))
    all_indices = sorted(set(key_indices + regular_indices))
    
    # Sample waypoints to find cities
    for i in all_indices:
        if i >= len(waypoints):
            continue
            
        waypoint = waypoints[i]
        lat = waypoint.get("lat")
        lon = waypoint.get("lon")
        
        if lat and lon:
            city_info = reverse_geocode(lat, lon)
            
            if city_info and city_info["name"]:
                city_name = city_info["name"]
                
                # Skip if already seen or if it's start/end city
                if (city_name.lower() not in seen_cities and 
                    city_name.lower() not in [start_city.lower(), end_city.lower()]):
                    
                    cities.append({
                        "name": city_name,
                        "lat": lat,
                        "lon": lon,
                        "state": city_info.get("state", "")
                    })
                    seen_cities.add(city_name.lower())
    
    return cities


def find_cities_along_route(
    start_city: str,
    end_city: str,
    threshold_km: float = 50
) -> List[Dict[str, Any]]:
    """
    Find major cities along the route between start and end cities.
    Uses Google Maps Directions API for actual driving route.
    
    Args:
        start_city: Starting city name
        end_city: Ending city name
        threshold_km: Maximum distance from direct route to consider a city (fallback mode)
        
    Returns:
        List of cities with their coordinates, ordered by distance from start
    """
    # Geocode start and end cities
    start_coords = geocode_location(start_city)
    end_coords = geocode_location(end_city)
    
    if not start_coords or not end_coords:
        logger.error("route.geocoding_failed", start=start_city, end=end_city)
        return []
    
    start_lat, start_lon = start_coords["lat"], start_coords["lon"]
    end_lat, end_lon = end_coords["lat"], end_coords["lon"]
    total_distance = calculate_distance(start_lat, start_lon, end_lat, end_lon)
    
    route_cities = []
    
    # Try to get actual route from Google Maps
    logger.info("route.using_google_maps", start=start_city, end=end_city)
    waypoints = get_route_from_google_maps(start_city, end_city)
    
    if waypoints and len(waypoints) > 0:
        # Found actual route! Extract cities from waypoints
        logger.info("route.google_maps_success", waypoints_count=len(waypoints))
        
        # Sample waypoints to find cities - sample every 5th waypoint
        route_cities = find_cities_from_route_waypoints(waypoints, start_city, end_city, sample_interval=5)
        
        # Calculate distance from start for each city
        for city in route_cities:
            if "distance_from_start" not in city:
                dist = calculate_distance(start_lat, start_lon, city["lat"], city["lon"])
                city["distance_from_start"] = round(dist, 2)
        
    else:
        # FALLBACK: Use predefined cities + straight-line interpolation
        logger.warning("route.google_maps_failed_using_fallback", start=start_city, end=end_city)
        
        # Check predefined major cities first
        for city_name, city_data in MAJOR_CITIES_INDIA.items():
            city_lat = city_data["lat"]
            city_lon = city_data["lon"]
            
            # Skip start and end cities
            if city_name.lower() in [start_city.lower(), end_city.lower()]:
                continue
            
            # Check if city is near the route
            if is_point_near_route(city_lat, city_lon, start_lat, start_lon, end_lat, end_lon, threshold_km):
                dist_from_start = calculate_distance(start_lat, start_lon, city_lat, city_lon)
                
                route_cities.append({
                    "name": city_name,
                    "lat": city_lat,
                    "lon": city_lon,
                    "state": city_data.get("state", ""),
                    "distance_from_start": round(dist_from_start, 2)
                })
        
        # If no cities found or route is long, add intermediate waypoints
        if len(route_cities) < 2 and total_distance > 100:
            # Generate intermediate points along the route
            num_points = min(5, max(2, int(total_distance / 100)))  # 1 point per 100km, max 5
            
            for i in range(1, num_points + 1):
                fraction = i / (num_points + 1)
                
                # Linear interpolation between start and end
                inter_lat = start_lat + (end_lat - start_lat) * fraction
                inter_lon = start_lon + (end_lon - start_lon) * fraction
                
                # Try to find actual city name at this location using reverse geocoding
                try:
                    city_info = reverse_geocode(inter_lat, inter_lon)
                    if city_info:
                        # Check if this city is already in our list
                        if not any(c["name"].lower() == city_info["name"].lower() for c in route_cities):
                            dist_from_start = calculate_distance(start_lat, start_lon, inter_lat, inter_lon)
                            route_cities.append({
                                "name": city_info["name"],
                                "lat": inter_lat,
                                "lon": inter_lon,
                                "state": city_info.get("state", ""),
                                "distance_from_start": round(dist_from_start, 2)
                            })
                except Exception as e:
                    logger.warning("route.reverse_geocode_failed", lat=inter_lat, lon=inter_lon, error=str(e))
    
    # Sort by distance from start
    route_cities.sort(key=lambda x: x["distance_from_start"])
    
    # AI Verification: Filter to only major cities using Gemini
    logger.info("route.cities_before_ai_filter", 
                start=start_city, 
                end=end_city,
                count=len(route_cities),
                cities=[c["name"] for c in route_cities])
    
    route_cities = verify_route_with_ai(start_city, end_city, route_cities)
    
    logger.info("route.cities_after_ai_filter", 
                start=start_city, 
                end=end_city,
                count=len(route_cities),
                cities=[c["name"] for c in route_cities])
    
    return route_cities


def reverse_geocode(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Reverse geocode coordinates to find city name.
    Uses OpenWeatherMap Geocoding API.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dictionary with city information or None
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        logger.warning("reverse_geocoding.no_api_key", lat=lat, lon=lon)
        return None
    
    try:
        url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                location_info = {
                    "name": data[0].get("name", ""),
                    "state": data[0].get("state", ""),
                    "country": data[0].get("country", "")
                }
                logger.info("reverse_geocoding.success", 
                           lat=lat, lon=lon, 
                           location=f"{location_info['name']}, {location_info['state']}")
                return location_info
            else:
                logger.warning("reverse_geocoding.no_results", lat=lat, lon=lon)
        else:
            logger.error("reverse_geocoding.api_error", 
                        lat=lat, lon=lon, 
                        status=response.status_code,
                        response=response.text[:200])
    except Exception as e:
        logger.error("reverse_geocoding.exception", lat=lat, lon=lon, error=str(e))
    
    return None


def get_route_weather_analysis(
    start_city: str,
    end_city: str,
    date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze weather conditions along a route between two cities.
    Uses Google Maps Directions API for accurate route detection.
    
    Args:
        start_city: Starting city name (e.g., "Chennai")
        end_city: Ending city name (e.g., "Trichy")
        date: Optional date for weather forecast (YYYY-MM-DD)
        
    Returns:
        Dictionary containing route analysis with weather for each city
    """
    try:
        # Geocode start and end
        start_coords = geocode_location(start_city)
        end_coords = geocode_location(end_city)
        
        if not start_coords or not end_coords:
            return {
                "success": False,
                "error": "Could not geocode start or end city"
            }
        
        # Calculate total route distance
        total_distance = calculate_distance(
            start_coords["lat"], start_coords["lon"],
            end_coords["lat"], end_coords["lon"]
        )
        
        # Find intermediate cities using Google Maps
        intermediate_cities = find_cities_along_route(start_city, end_city)
        
        # Build complete route: start → intermediates → end
        all_cities = [
            {
                "name": start_coords["name"],
                "lat": start_coords["lat"],
                "lon": start_coords["lon"],
                "state": start_coords.get("state", ""),
                "distance_from_start": 0,
                "is_start": True
            }
        ]
        
        all_cities.extend(intermediate_cities)
        
        all_cities.append({
            "name": end_coords["name"],
            "lat": end_coords["lat"],
            "lon": end_coords["lon"],
            "state": end_coords.get("state", ""),
            "distance_from_start": round(total_distance, 2),
            "is_end": True
        })
        
        # Fetch weather for each city
        city_weather = []
        weather_warnings = []
        severe_conditions = []
        
        for city in all_cities:
            try:
                weather = get_weather_data(city["name"])
                
                if isinstance(weather, dict) and weather.get("success"):
                    # Assess weather severity
                    severity = assess_weather_severity(weather)
                    
                    city_data = {
                        "city": city["name"],
                        "state": city.get("state", ""),
                        "distance_km": city["distance_from_start"],
                        "weather": weather,
                        "severity": severity,
                        "is_start": city.get("is_start", False),
                        "is_end": city.get("is_end", False)
                    }
                    
                    city_weather.append(city_data)
                    
                    # Track warnings and severe conditions (only high/critical)
                    if severity in ["high", "critical"]:
                        severe_conditions.append(f"{city['name']}: {weather.get('condition', 'Unknown')}")
                    
                    # Only warn about truly dangerous winds
                    if weather.get("wind_speed", 0) > 40:
                        weather_warnings.append(f"Strong winds in {city['name']} ({weather.get('wind_speed')} km/h)")
                    
                    # Only warn about heavy rain
                    condition_lower = weather.get("condition", "").lower()
                    if "heavy rain" in condition_lower or "thunderstorm" in condition_lower:
                        weather_warnings.append(f"Heavy rain in {city['name']}")
                        
            except Exception as e:
                logger.warning("route.weather_fetch_failed", city=city["name"], error=str(e))
        
        # Generate route recommendation
        recommendation = generate_route_recommendation(city_weather, weather_warnings, severe_conditions)
        
        return {
            "success": True,
            "route": {
                "start": start_city,
                "end": end_city,
                "total_distance_km": round(total_distance, 2),
                "cities_count": len(all_cities)
            },
            "cities": city_weather,
            "weather_warnings": weather_warnings,
            "severe_conditions": severe_conditions,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("route.analysis_failed", start=start_city, end=end_city, error=str(e))
        return {
            "success": False,
            "error": str(e)
        }


def assess_weather_severity(weather: Dict[str, Any]) -> str:
    """
    Assess weather severity based on conditions.
    Only severe/critical conditions trigger high ratings.
    
    Args:
        weather: Weather data dictionary
        
    Returns:
        Severity level: "low", "medium", "high", "critical"
    """
    condition = weather.get("condition", "").lower()
    wind_speed = weather.get("wind_speed", 0)
    temp = weather.get("temperature", 25)
    
    # CRITICAL - DO NOT TRAVEL (Red Alert)
    if any(word in condition for word in ["thunderstorm", "tornado", "hurricane", "cyclone", "severe storm"]):
        return "critical"
    
    if temp > 48 or temp < -5:  # Extreme temperatures
        return "critical"
    
    if wind_speed > 60:  # Hurricane-force winds
        return "critical"
    
    # HIGH - AVOID TRAVEL IF POSSIBLE (Orange Alert)
    if any(word in condition for word in ["heavy rain", "heavy snow", "blizzard", "hail", "ice storm"]):
        return "high"
    
    if temp > 43 or temp < 2:  # Very hot or near freezing
        return "high"
    
    if wind_speed > 40:  # Very strong winds
        return "high"
    
    # MEDIUM - PROCEED WITH CAUTION (Yellow - minor conditions)
    if any(word in condition for word in ["moderate rain", "light snow", "fog", "mist"]):
        return "medium"
    
    if temp > 38 or temp < 8:  # Uncomfortable but manageable
        return "medium"
    
    if wind_speed > 25:  # Moderate winds
        return "medium"
    
    # LOW - SAFE TO TRAVEL (Green)
    # Light clouds, clear, partly cloudy, scattered clouds, light drizzle - all safe
    return "low"


def generate_route_recommendation(
    city_weather: List[Dict[str, Any]],
    warnings: List[str],
    severe: List[str]
) -> str:
    """
    Generate travel recommendation based on route weather analysis.
    Only severe/critical conditions trigger travel warnings.
    
    Args:
        city_weather: List of cities with weather data
        warnings: List of weather warnings
        severe: List of severe conditions
        
    Returns:
        Recommendation string
    """
    if not city_weather:
        return "Unable to generate recommendation - no weather data available."
    
    # Count severity levels
    severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for city in city_weather:
        severity = city.get("severity", "low")
        severity_counts[severity] += 1
    
    total_cities = len(city_weather)
    
    # CRITICAL - DO NOT TRAVEL
    if severity_counts["critical"] > 0:
        critical_cities = [c["city"] for c in city_weather if c.get("severity") == "critical"]
        return (
            f"🚨 DO NOT TRAVEL - Critical weather conditions detected in {', '.join(critical_cities)}. "
            f"Extreme weather poses serious safety risks (severe storms, extreme temperatures, or hurricane-force winds). "
            f"POSTPONE TRAVEL or take alternative route."
        )
    
    # HIGH - TRAVEL NOT RECOMMENDED
    if severity_counts["high"] >= 2:
        high_cities = [c["city"] for c in city_weather if c.get("severity") == "high"]
        return (
            f"⚠️ TRAVEL NOT RECOMMENDED - Hazardous weather in {', '.join(high_cities)}. "
            f"Heavy rain, snow, or very strong winds expected. Consider delaying travel until conditions improve."
        )
    
    if severity_counts["high"] == 1:
        high_city = next(c["city"] for c in city_weather if c.get("severity") == "high")
        return (
            f"⚠️ CAUTION ADVISED - Hazardous weather expected in {high_city}. "
            f"Travel possible but drive carefully through this area. Monitor weather updates."
        )
    
    # MEDIUM - SAFE WITH CAUTION
    if severity_counts["medium"] >= total_cities * 0.5:  # More than half have medium severity
        return (
            f"✅ TRAVEL SAFE WITH CAUTION - Some areas may have moderate rain, fog, or winds. "
            f"Normal travel possible, just drive carefully and stay alert to changing conditions."
        )
    
    # LOW - EXCELLENT CONDITIONS
    return (
        f"✅ EXCELLENT CONDITIONS - Weather is favorable for travel along this route. "
        f"Safe journey expected. Enjoy your trip!"
    )
