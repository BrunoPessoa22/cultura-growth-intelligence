#!/usr/bin/env python3
"""Test Amplitude API connection"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('AMPLITUDE_API_KEY')
secret_key = os.getenv('AMPLITUDE_SECRET_KEY')

print(f"API Key: {api_key[:20]}...")
print(f"Secret Key: {secret_key[:10]}...")

# The issue: ampex_ keys are EXPORT API keys, not Dashboard API keys
print(f"\n🔍 Key Type: {'Export API Key' if api_key.startswith('ampex_') else 'Project/Dashboard API Key'}")

if api_key.startswith('ampex_'):
    print("\n⚠️  FOUND THE PROBLEM!")
    print("You have an EXPORT API key (ampex_), but we need a PROJECT API key.")
    print("\nThe Export API is for raw event data export, not for analytics queries.")
    print("\n📍 Where to find the correct keys:")
    print("1. Go to: https://analytics.amplitude.com")
    print("2. Settings → Projects → [Your Project]")
    print("3. Look for TWO different key sections:")
    print("   - PROJECT API KEY (use this one!)")
    print("   - Export API Key (ampex_ - this is what you have)")
    print("\n4. The PROJECT API KEY should NOT start with 'ampex_'")
    print("5. Copy BOTH the Project API Key and Secret Key")

print("\n" + "="*60)
print("Testing Export API (what you have now):")
print("="*60)

# Test Export API
url = "https://amplitude.com/api/2/export"
params = {
    'start': '20251101T00',
    'end': '20251110T00'
}
response = requests.get(url, params=params, auth=(api_key, secret_key))
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Export API works! (But we need Project API for analytics)")
else:
    print(f"Response: {response.text[:300]}")

print("\n" + "="*60)
print("What we need: Project API for Analytics Queries")
print("="*60)
print("This allows us to query:")
print("- User cohorts by campaign")
print("- Activation rates")
print("- Retention metrics")
print("- Revenue per cohort")
