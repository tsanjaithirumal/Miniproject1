import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT running (Connection Refused)")

def main():
    print("Testing Backend Health...")
    test_health()
    print("\nTo run the full application:")
    print("1. Backend: uvicorn app.main:app --reload")
    print("2. Frontend: npm run dev")

if __name__ == "__main__":
    main()
