#!/usr/bin/env python3
"""Test social media validation against weather data"""
from dotenv import load_dotenv
load_dotenv()

from src.tools.custom_tools import get_social_media_reports, validate_social_media_reports

# Test location
location = "Chennai"

print(f"🔍 Testing Social Media Validation for {location}\n")
print("=" * 80)

# Step 1: Get social media reports
print(f"\n📱 Step 1: Fetching social media reports for {location}...")
reports = get_social_media_reports(location)
print(f"\n{reports}\n")

# Step 2: Validate the reports
print("=" * 80)
print(f"\n✅ Step 2: Validating reports against official weather data...\n")
validation_result = validate_social_media_reports(location, reports)
print(validation_result)

print("\n" + "=" * 80)
print("✅ Test complete! The social media agent will now automatically validate reports.")
