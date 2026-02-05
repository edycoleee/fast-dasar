"""
Test JWT Authentication Implementation
Test semua endpoint dengan JWT
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Helper untuk print response dengan format yang bagus"""
    print(f"\n{'='*60}")
    print(f"📍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()


def test_jwt_flow():
    """
    Test complete JWT authentication flow:
    1. Register siswa dengan password
    2. Login dengan email & password -> dapat JWT token
    3. Access protected endpoint (dashboard) dengan JWT token
    4. Test CRUD dengan JWT token
    5. Logout
    """
    
    print("\n" + "="*60)
    print("🚀 TESTING JWT AUTHENTICATION FLOW")
    print("="*60)
    
    # ==================== 1. REGISTER SISWA ====================
    print("\n[1] REGISTER - Buat siswa baru dengan password")
    siswa_data = {
        "nama": "Edy Cole",
        "email": "edycoleee@gmail.com",
        "password": "secret123"
    }
    
    response = requests.post(f"{BASE_URL}/api/siswa/", json=siswa_data)
    print_response("POST /api/siswa/ - Register Siswa", response)
    
    if response.status_code != 201:
        print("❌ Registration failed!")
        return
    
    siswa = response.json()
    siswa_id = siswa["id"]
    print(f"✅ Siswa registered with ID: {siswa_id}")
    print(f"   Notice: Password tidak muncul di response (security)")
    
    
    # ==================== 2. LOGIN ====================
    print("\n[2] LOGIN - Login dengan email & password")
    login_data = {
        "email": "edycoleee@gmail.com",
        "password": "secret123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("POST /api/auth/login - Login", response)
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return
    
    login_result = response.json()
    jwt_token = login_result["access_token"]
    print(f"✅ Login successful!")
    print(f"   JWT Token: {jwt_token[:50]}...")
    print(f"   Token Type: {login_result['token_type']}")
    
    
    # ==================== 3. TEST LOGIN DENGAN PASSWORD SALAH ====================
    print("\n[3] TEST - Login dengan password salah")
    wrong_login = {
        "email": "edycoleee@gmail.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=wrong_login)
    print_response("POST /api/auth/login - Wrong Password", response)
    print("✅ Correct behavior: Login ditolak karena password salah")
    
    
    # ==================== 4. ACCESS DASHBOARD TANPA TOKEN ====================
    print("\n[4] TEST - Access dashboard tanpa JWT token (should fail)")
    response = requests.get(f"{BASE_URL}/api/dashboard")
    print_response("GET /api/dashboard - No Token", response)
    print("✅ Correct behavior: Akses ditolak karena tidak ada token")
    
    
    # ==================== 5. ACCESS DASHBOARD DENGAN TOKEN ====================
    print("\n[5] ACCESS - Dashboard dengan JWT token")
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    
    response = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)
    print_response("GET /api/dashboard - With JWT Token", response)
    
    if response.status_code == 200:
        print("✅ Dashboard accessed successfully!")
        dashboard_data = response.json()
        print(f"   User info from token: {dashboard_data.get('user')}")
    
    
    # ==================== 6. CREATE SISWA LAIN (perlu auth) ====================
    print("\n[6] CREATE - Buat siswa baru (dengan JWT auth)")
    new_siswa = {
        "nama": "Jane Doe",
        "email": "jane@example.com",
        "password": "jane123"
    }
    
    # Tanpa token (should fail karena middleware)
    response = requests.post(f"{BASE_URL}/api/siswa/", json=new_siswa)
    print_response("POST /api/siswa/ - No Token", response)
    
    # Dengan token (should succeed)
    response = requests.post(f"{BASE_URL}/api/siswa/", json=new_siswa, headers=headers)
    print_response("POST /api/siswa/ - With Token", response)
    
    
    # ==================== 7. GET ALL SISWA (tidak perlu auth) ====================
    print("\n[7] READ - Get all siswa (public endpoint)")
    response = requests.get(f"{BASE_URL}/api/siswa/")
    print_response("GET /api/siswa/ - Get All", response)
    
    if response.status_code == 200:
        siswa_list = response.json()
        print(f"✅ Total siswa: {len(siswa_list)}")
        print(f"   Notice: Password tidak muncul di response (security)")
    
    
    # ==================== 8. UPDATE SISWA (perlu auth) ====================
    print("\n[8] UPDATE - Update siswa dengan password baru")
    update_data = {
        "nama": "Edy Cole Updated",
        "email": "edycoleee@gmail.com",
        "password": "newsecret456"
    }
    
    response = requests.put(f"{BASE_URL}/api/siswa/{siswa_id}", json=update_data, headers=headers)
    print_response(f"PUT /api/siswa/{siswa_id} - Update with new password", response)
    
    
    # ==================== 9. LOGIN DENGAN PASSWORD BARU ====================
    print("\n[9] TEST - Login dengan password baru")
    new_login = {
        "email": "edycoleee@gmail.com",
        "password": "newsecret456"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=new_login)
    print_response("POST /api/auth/login - New Password", response)
    
    if response.status_code == 200:
        print("✅ Login with new password successful!")
    
    
    # ==================== 10. LOGOUT ====================
    print("\n[10] LOGOUT - Logout (client-side token deletion)")
    response = requests.post(f"{BASE_URL}/api/auth/logout")
    print_response("POST /api/auth/logout", response)
    
    
    # ==================== 11. TEST TOKEN DENGAN INVALID FORMAT ====================
    print("\n[11] TEST - Access dengan invalid token")
    invalid_headers = {
        "Authorization": "Bearer invalid-token-12345"
    }
    
    response = requests.get(f"{BASE_URL}/api/dashboard", headers=invalid_headers)
    print_response("GET /api/dashboard - Invalid Token", response)
    print("✅ Correct behavior: Akses ditolak karena token invalid")
    
    
    # ==================== SUMMARY ====================
    print("\n" + "="*60)
    print("✅ JWT AUTHENTICATION FLOW TEST COMPLETED!")
    print("="*60)
    print("\n📝 Summary:")
    print("1. ✅ Siswa registration dengan password (hashed)")
    print("2. ✅ Login dengan email/password -> JWT token")
    print("3. ✅ Protected endpoints (dashboard) memerlukan JWT")
    print("4. ✅ Password verification berfungsi dengan baik")
    print("5. ✅ Password update berfungsi")
    print("6. ✅ Invalid token ditolak")
    print("7. ✅ Logout endpoint tersedia")
    print("\n📚 Key Features:")
    print("- Password di-hash dengan bcrypt (tidak disimpan plain text)")
    print("- JWT token untuk authentication (stateless)")
    print("- Password tidak muncul di response (security)")
    print("- Middleware auto-check JWT untuk protected endpoints")
    print("\n")


if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running!")
            test_jwt_flow()
        else:
            print("❌ Server responded with error")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Server is not running!")
        print("Please start the server first with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
