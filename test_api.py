import requests
import json

BASE_URL = "http://localhost:5000"

def test_basic():
    print("=== BASIC API TEST ===")
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        r = requests.get(BASE_URL)
        print(f"   Status: {r.status_code}")
        if "Movie Sentiment Analysis API" in r.text:
            print("   ✅ API is running")
        else:
            print("   ❌ Unexpected response")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Predict endpoint (expecting 400 or 500 due to database)
    print("\n2. Testing predict endpoint...")
    test_data = {"text": "This movie is absolutely fantastic!"}
    
    try:
        r = requests.post(
            f"{BASE_URL}/predict",
            json=test_data,
            timeout=5
        )
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print(f"   ✅ SUCCESS: {r.json()}")
        elif r.status_code == 400:
            print("   ⚠️  Bad Request (might be database issue)")
            print(f"   Response: {r.text}")
        elif r.status_code == 500:
            print("   ⚠️  Internal Server Error (database issue)")
            print(f"   Response: {r.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Health endpoint
    print("\n3. Testing health endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_basic()

