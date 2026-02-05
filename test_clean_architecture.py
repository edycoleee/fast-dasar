"""
Test Clean Architecture Implementation
Quick test to verify all endpoints work correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(BASE_URL)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_create_admin():
    """Create admin user"""
    print("\n=== Creating Admin User ===")
    data = {
        "nama": "Admin User",
        "email": "admin@test.com",
        "password": "admin123",
        "role": "admin"
    }
    
    # Try to create (might already exist)
    try:
        response = requests.post(f"{API_V1}/users/", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Note: {e}")
        return True  # User might already exist


def test_create_regular_user():
    """Create regular user"""
    print("\n=== Creating Regular User ===")
    data = {
        "nama": "Regular User",
        "email": "user@test.com",
        "password": "user123",
        "role": "user"
    }
    
    try:
        response = requests.post(f"{API_V1}/users/", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Note: {e}")
        return True


def test_login_admin():
    """Test admin login"""
    print("\n=== Testing Admin Login ===")
    data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{API_V1}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if response.status_code == 200:
        return result.get("access_token")
    return None


def test_login_user():
    """Test user login"""
    print("\n=== Testing User Login ===")
    data = {
        "email": "user@test.com",
        "password": "user123"
    }
    
    response = requests.post(f"{API_V1}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if response.status_code == 200:
        return result.get("access_token")
    return None


def test_dashboard(token):
    """Test protected dashboard"""
    print("\n=== Testing Dashboard (Protected) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_V1}/auth/dashboard", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_get_all_users(token):
    """Test get all users"""
    print("\n=== Testing Get All Users ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_V1}/users/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_update_role(admin_token, user_id):
    """Test update user role (admin only)"""
    print(f"\n=== Testing Update Role (Admin Only) ===")
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"role": "user"}
    
    response = requests.patch(
        f"{API_V1}/admin/{user_id}/role",
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_logout(token):
    """Test logout"""
    print("\n=== Testing Logout ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{API_V1}/auth/logout", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def main():
    """Run all tests"""
    print("=" * 60)
    print("CLEAN ARCHITECTURE - API TESTING")
    print("=" * 60)
    
    # Test root
    test_root()
    
    # Create users (without auth for first time)
    # Note: In production, you'd want to protect these endpoints
    # test_create_admin()
    # test_create_regular_user()
    
    # Login as admin
    admin_token = test_login_admin()
    if not admin_token:
        print("\n❌ Admin login failed. Please create admin user first.")
        return
    
    # Login as user
    user_token = test_login_user()
    if not user_token:
        print("\n❌ User login failed. Please create user first.")
        return
    
    # Test protected endpoints
    test_dashboard(admin_token)
    test_dashboard(user_token)
    
    # Test CRUD
    test_get_all_users(admin_token)
    
    # Test admin-only operation
    # test_update_role(admin_token, 2)
    
    # Test logout
    test_logout(admin_token)
    test_logout(user_token)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
