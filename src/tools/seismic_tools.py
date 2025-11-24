"""
Seismic and Tsunami Monitoring Tools
Uses USGS Earthquake API and NOAA Tsunami Warning System
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import requests
import structlog
from dotenv import load_dotenv

load_dotenv()
logger = structlog.get_logger("seismic_tools")


def get_earthquake_data(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: int = 500,
    min_magnitude: float = 2.5,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get earthquake data from USGS Earthquake API.
    
    Args:
        latitude: Center latitude for search (optional)
        longitude: Center longitude for search (optional)
        radius_km: Search radius in kilometers (default 500km)
        min_magnitude: Minimum earthquake magnitude (default 2.5)
        days: Number of days to look back (default 7)
        
    Returns:
        Dictionary with earthquake data
    """
    try:
        base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        params = {
            "format": "geojson",
            "starttime": start_time.strftime("%Y-%m-%d"),
            "endtime": end_time.strftime("%Y-%m-%d"),
            "minmagnitude": min_magnitude,
            "orderby": "magnitude"
        }
        
        # Add location-based filtering if coordinates provided
        if latitude is not None and longitude is not None:
            params["latitude"] = latitude
            params["longitude"] = longitude
            params["maxradiuskm"] = radius_km
        
        response = requests.get(base_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            earthquakes = []
            
            for feature in data.get("features", []):
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                coordinates = geometry.get("coordinates", [])
                
                earthquake = {
                    "magnitude": properties.get("mag"),
                    "location": properties.get("place"),
                    "time": datetime.fromtimestamp(properties.get("time", 0) / 1000).isoformat(),
                    "depth_km": coordinates[2] if len(coordinates) > 2 else None,
                    "latitude": coordinates[1] if len(coordinates) > 1 else None,
                    "longitude": coordinates[0] if len(coordinates) > 0 else None,
                    "tsunami": properties.get("tsunami", 0) == 1,
                    "alert": properties.get("alert"),
                    "significance": properties.get("sig"),
                    "url": properties.get("url"),
                    "felt_reports": properties.get("felt"),
                    "type": properties.get("type")
                }
                earthquakes.append(earthquake)
            
            # Sort by magnitude (highest first)
            earthquakes.sort(key=lambda x: x.get("magnitude", 0), reverse=True)
            
            logger.info("earthquake_data.fetched", 
                       count=len(earthquakes),
                       max_magnitude=earthquakes[0].get("magnitude") if earthquakes else None)
            
            return {
                "success": True,
                "count": len(earthquakes),
                "earthquakes": earthquakes,
                "search_params": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius_km": radius_km,
                    "min_magnitude": min_magnitude,
                    "days": days
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error("earthquake_data.api_error", status=response.status_code)
            return {
                "success": False,
                "error": f"USGS API error: {response.status_code}",
                "earthquakes": []
            }
            
    except Exception as e:
        logger.error("earthquake_data.exception", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "earthquakes": []
        }


def assess_earthquake_risk(magnitude: float, depth_km: float, distance_km: float = 0) -> Dict[str, Any]:
    """
    Assess earthquake risk level based on magnitude, depth, and distance.
    
    Args:
        magnitude: Earthquake magnitude (Richter scale)
        depth_km: Depth in kilometers
        distance_km: Distance from location in km
        
    Returns:
        Risk assessment dictionary
    """
    # Magnitude-based severity
    if magnitude >= 8.0:
        severity = "critical"
        impact = "Great earthquake - severe damage over large area"
    elif magnitude >= 7.0:
        severity = "critical"
        impact = "Major earthquake - serious damage over wide area"
    elif magnitude >= 6.0:
        severity = "high"
        impact = "Strong earthquake - damage to buildings and structures"
    elif magnitude >= 5.0:
        severity = "medium"
        impact = "Moderate earthquake - felt widely, minor damage possible"
    elif magnitude >= 4.0:
        severity = "low"
        impact = "Light earthquake - felt by many, no significant damage"
    else:
        severity = "minimal"
        impact = "Minor earthquake - often not felt"
    
    # Adjust for depth (shallow earthquakes more dangerous)
    if depth_km < 70:
        depth_category = "shallow"
        depth_note = "Shallow earthquakes cause more surface damage"
    elif depth_km < 300:
        depth_category = "intermediate"
        depth_note = "Moderate depth reduces surface impact"
    else:
        depth_category = "deep"
        depth_note = "Deep earthquakes have minimal surface impact"
    
    # Adjust for distance
    if distance_km < 50:
        proximity = "very_close"
        proximity_note = "Within immediate danger zone"
    elif distance_km < 100:
        proximity = "close"
        proximity_note = "Within affected area"
    elif distance_km < 300:
        proximity = "moderate"
        proximity_note = "May feel shaking"
    else:
        proximity = "far"
        proximity_note = "Unlikely to be affected"
    
    # Generate recommendations
    recommendations = []
    if magnitude >= 5.0 and distance_km < 100:
        recommendations.append("🚨 DROP, COVER, and HOLD ON during shaking")
        recommendations.append("🏠 Check for structural damage after earthquake")
        recommendations.append("📻 Monitor emergency broadcasts")
    
    if magnitude >= 6.0 and distance_km < 200:
        recommendations.append("⚠️ Be prepared for aftershocks")
        recommendations.append("🔥 Check for gas leaks and fire hazards")
        recommendations.append("💧 Have emergency water and supplies ready")
    
    if magnitude >= 7.0:
        recommendations.append("🚨 EVACUATE if buildings are damaged")
        recommendations.append("📱 Contact emergency services if needed")
        recommendations.append("👥 Check on neighbors and family")
    
    return {
        "magnitude": magnitude,
        "severity": severity,
        "impact": impact,
        "depth_km": depth_km,
        "depth_category": depth_category,
        "depth_note": depth_note,
        "distance_km": distance_km,
        "proximity": proximity,
        "proximity_note": proximity_note,
        "recommendations": recommendations
    }


def get_tsunami_warnings(latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
    """
    Get tsunami warnings from NOAA/NWS.
    Note: This is a simplified implementation. Full integration would require NOAA API access.
    
    Args:
        latitude: Latitude for location-specific warnings
        longitude: Longitude for location-specific warnings
        
    Returns:
        Dictionary with tsunami warning data
    """
    try:
        # NOAA National Weather Service API for alerts
        base_url = "https://api.weather.gov/alerts/active"
        
        params = {
            "event": "Tsunami Warning,Tsunami Watch,Tsunami Advisory"
        }
        
        if latitude is not None and longitude is not None:
            params["point"] = f"{latitude},{longitude}"
        
        response = requests.get(base_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            
            warnings = []
            for feature in features:
                properties = feature.get("properties", {})
                
                warning = {
                    "event": properties.get("event"),
                    "severity": properties.get("severity"),
                    "certainty": properties.get("certainty"),
                    "urgency": properties.get("urgency"),
                    "headline": properties.get("headline"),
                    "description": properties.get("description"),
                    "instruction": properties.get("instruction"),
                    "areas": properties.get("areaDesc"),
                    "onset": properties.get("onset"),
                    "expires": properties.get("expires"),
                    "sender": properties.get("senderName")
                }
                warnings.append(warning)
            
            has_warning = any(w.get("event") == "Tsunami Warning" for w in warnings)
            has_watch = any(w.get("event") == "Tsunami Watch" for w in warnings)
            has_advisory = any(w.get("event") == "Tsunami Advisory" for w in warnings)
            
            logger.info("tsunami_warnings.fetched", count=len(warnings))
            
            return {
                "success": True,
                "has_warning": has_warning,
                "has_watch": has_watch,
                "has_advisory": has_advisory,
                "warnings": warnings,
                "count": len(warnings),
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.warning("tsunami_warnings.api_error", status=response.status_code)
            return {
                "success": True,
                "has_warning": False,
                "has_watch": False,
                "has_advisory": False,
                "warnings": [],
                "count": 0,
                "message": "No active tsunami warnings"
            }
            
    except Exception as e:
        logger.error("tsunami_warnings.exception", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "warnings": [],
            "count": 0
        }


def fact_check_earthquake_claim(user_claim: str, latitude: float, longitude: float, location: str) -> Dict[str, Any]:
    """
    Fact-check earthquake claims against USGS data.
    
    Args:
        user_claim: User's earthquake claim
        latitude: Location latitude
        longitude: Location longitude
        location: Location name
        
    Returns:
        Verification results
    """
    import re
    
    # Get recent earthquake data for the region
    earthquake_data = get_earthquake_data(latitude, longitude, radius_km=500, days=7, min_magnitude=2.0)
    
    user_claim_lower = user_claim.lower()
    earthquakes = earthquake_data.get("earthquakes", [])
    
    matches = []
    discrepancies = []
    verdict = "UNVERIFIED"
    confidence = 50
    
    # Check for earthquake claims
    if any(word in user_claim_lower for word in ["earthquake", "quake", "tremor", "seismic", "shaking"]):
        if earthquakes and len(earthquakes) > 0:
            recent_eq = earthquakes[0]  # Most significant recent earthquake
            mag = recent_eq.get("magnitude", 0)
            
            # Check magnitude claims
            magnitude_match = re.search(r"(\d+\.?\d*)\s*(?:magnitude|richter|m)", user_claim_lower)
            claimed_mag = float(magnitude_match.group(1)) if magnitude_match else None
            
            if claimed_mag:
                if abs(claimed_mag - mag) < 0.5:
                    matches.append(f"✓ Earthquake magnitude {mag} confirmed (claimed: {claimed_mag})")
                    verdict = "VERIFIED"
                    confidence = 90
                elif abs(claimed_mag - mag) < 1.0:
                    matches.append(f"⚠ Earthquake detected (magnitude {mag}, claimed: {claimed_mag})")
                    verdict = "PARTIALLY TRUE"
                    confidence = 70
                else:
                    discrepancies.append(f"✗ Claimed magnitude {claimed_mag} doesn't match recorded {mag}")
                    verdict = "FALSE"
                    confidence = 20
            else:
                # General earthquake claim
                matches.append(f"✓ Earthquake confirmed: Magnitude {mag} at {recent_eq.get('location')}")
                if mag >= 5.0:
                    matches.append(f"✓ Significant earthquake detected")
                verdict = "VERIFIED"
                confidence = 85
            
            # Add details
            time_str = recent_eq.get("time", "")
            if time_str:
                try:
                    eq_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    hours_ago = (datetime.now() - eq_time.replace(tzinfo=None)).total_seconds() / 3600
                    if hours_ago < 24:
                        matches.append(f"📅 Occurred {int(hours_ago)} hours ago")
                except:
                    pass
        else:
            discrepancies.append(f"✗ No significant earthquakes detected in the region (past 7 days)")
            verdict = "FALSE"
            confidence = 15
    
    # Check for tsunami claims
    if any(word in user_claim_lower for word in ["tsunami", "tidal wave"]):
        tsunami_data = get_tsunami_warnings(latitude, longitude)
        has_warning = tsunami_data.get("has_warning", False)
        
        if has_warning:
            matches.append("✓ TSUNAMI WARNING ACTIVE")
            verdict = "VERIFIED"
            confidence = 95
        else:
            # Check if any recent earthquakes had tsunami potential
            tsunami_eq = [eq for eq in earthquakes if eq.get("tsunami")]
            if tsunami_eq:
                matches.append(f"⚠ Tsunami-potential earthquake detected but no official warning")
                verdict = "PARTIALLY TRUE"
                confidence = 60
            else:
                discrepancies.append("✗ No tsunami warnings or tsunami-capable earthquakes detected")
                verdict = "FALSE"
                confidence = 10
    
    # Build official summary
    official_summary = "No significant seismic activity"
    if earthquakes:
        recent = earthquakes[0]
        official_summary = f"Most recent: Magnitude {recent.get('magnitude')} at {recent.get('location')}, Depth: {recent.get('depth_km')}km"
    
    return {
        "verdict": verdict,
        "confidence": confidence,
        "matches": matches,
        "discrepancies": discrepancies,
        "official_summary": official_summary,
        "recent_earthquakes": earthquakes[:3]  # Top 3 most significant
    }
