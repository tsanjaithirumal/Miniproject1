"""Simple script to test the registration endpoint"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_register():
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    print(f"Testing registration endpoint: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Registration successful!")
        else:
            print(f"\n❌ Registration failed with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("   Make sure the backend is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_register()

