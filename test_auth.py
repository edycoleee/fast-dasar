"""
Test Script untuk Authentication Flow
Demonstrasi cara kerja login dan protected endpoint
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_login_success():
    """Test login dengan credentials yang benar"""
    print_section("TEST 1: Login Success")
    
    url = f"{BASE_URL}/api/auth/login"
    payload = {
        "username": "admin",
        "password": "admin"
    }
    
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        token = response.json()["token"]
        print(f"\n✅ Login successful! Token: {token}")
        return token
    else:
        print("\n❌ Login failed!")
        return None


def test_login_failed():
    """Test login dengan credentials yang salah"""
    print_section("TEST 2: Login Failed (Wrong Password)")
    
    url = f"{BASE_URL}/api/auth/login"
    payload = {
        "username": "admin",
        "password": "wrong-password"
    }
    
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("\n✅ Correctly rejected invalid credentials")
    else:
        print("\n❌ Unexpected response")


def test_landing_without_token():
    """Test akses landing page tanpa token"""
    print_section("TEST 3: Access Landing WITHOUT Token")
    
    url = f"{BASE_URL}/api/landing"
    
    print(f"GET {url}")
    print("Headers: (no Authorization header)\n")
    
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("\n✅ Correctly rejected - unauthorized")
    else:
        print("\n❌ Should have been rejected!")


def test_landing_with_wrong_token():
    """Test akses landing page dengan token salah"""
    print_section("TEST 4: Access Landing WITH Wrong Token")
    
    url = f"{BASE_URL}/api/landing"
    headers = {
        "Authorization": "Bearer wrong-token-123"
    }
    
    print(f"GET {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}\n")
    
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("\n✅ Correctly rejected - invalid token")
    else:
        print("\n❌ Should have been rejected!")


def test_landing_with_valid_token(token):
    """Test akses landing page dengan token yang benar"""
    print_section("TEST 5: Access Landing WITH Valid Token")
    
    url = f"{BASE_URL}/api/landing"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"GET {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}\n")
    
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ Successfully accessed protected endpoint!")
    else:
        print("\n❌ Should have been successful!")


def test_complete_flow():
    """Test complete authentication flow"""
    print_section("TEST 6: Complete Authentication Flow")
    
    # Step 1: Login
    print("Step 1: Login to get token...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return
    
    token = login_response.json()["token"]
    print(f"✅ Got token: {token}\n")
    
    # Step 2: Access protected endpoint
    print("Step 2: Access protected endpoint with token...")
    landing_response = requests.get(
        f"{BASE_URL}/api/landing",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if landing_response.status_code != 200:
        print("❌ Access denied!")
        return
    
    print(f"✅ Access granted!")
    print(f"User info: {json.dumps(landing_response.json()['user'], indent=2)}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  🔐 AUTHENTICATION FLOW TEST SUITE")
    print("  FastAPI Login & Middleware Demo")
    print("="*60)
    
    try:
        # Test 1: Successful login
        token = test_login_success()
        
        # Test 2: Failed login
        test_login_failed()
        
        # Test 3: Access without token
        test_landing_without_token()
        
        # Test 4: Access with wrong token
        test_landing_with_wrong_token()
        
        # Test 5: Access with valid token
        if token:
            test_landing_with_valid_token(token)
        
        # Test 6: Complete flow
        test_complete_flow()
        
        # Summary
        print_section("🎉 All Tests Completed!")
        print("Lihat output di atas untuk melihat cara kerja authentication flow.")
        print("\nYang Anda pelajari:")
        print("1. ✅ Login endpoint (POST /api/auth/login)")
        print("2. ✅ Token generation dan response")
        print("3. ✅ Protected endpoint (GET /api/landing)")
        print("4. ✅ Bearer token authentication")
        print("5. ✅ Middleware validation flow")
        print("6. ✅ Error handling (401 Unauthorized)")
        print("\nNext: Upgrade ke JWT untuk production-ready authentication! 🚀\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure FastAPI server is running:")
        print("  uvicorn main:app --reload")
        print()


if __name__ == "__main__":
    main()
