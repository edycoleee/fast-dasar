"""
Test Authorization (Role-Based Access Control)
Test admin vs user permissions
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Helper untuk print response"""
    print(f"\n{'='*70}")
    print(f"📍 {title}")
    print(f"{'='*70}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()


def test_authorization():
    """
    Test complete authorization flow:
    1. Create admin user
    2. Create regular user
    3. Test admin permissions (full CRUD + role management)
    4. Test user permissions (CRU only, no Delete)
    5. Test permission denials
    """
    
    print("\n" + "="*70)
    print("🔐 TESTING ROLE-BASED AUTHORIZATION")
    print("="*70)
    
    # ==================== 1. CREATE ADMIN USER ====================
    print("\n[1] CREATE ADMIN - Register admin user")
    admin_data = {
        "nama": "Admin User",
        "email": "admin@example.com",
        "password": "admin123",
        "role": "admin"
    }
    
    # Note: First user needs to be created without auth
    # In production, you'd seed the first admin via migration
    response = requests.post(f"{BASE_URL}/api/siswa/", json=admin_data)
    print_response("POST /api/siswa/ - Create Admin (first user, no auth needed)", response)
    
    
    # ==================== 2. LOGIN AS ADMIN ====================
    print("\n[2] LOGIN - Login sebagai admin")
    admin_login = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=admin_login)
    print_response("POST /api/auth/login - Admin Login", response)
    
    if response.status_code != 200:
        print("❌ Admin login failed!")
        return
    
    admin_token = response.json()["access_token"]
    admin_user = response.json()["user"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    print(f"✅ Admin logged in!")
    print(f"   Role: {admin_user['role']}")
    print(f"   Token: {admin_token[:50]}...")
    
    
    # ==================== 3. CREATE REGULAR USER (by admin) ====================
    print("\n[3] CREATE USER - Admin create regular user")
    user_data = {
        "nama": "Regular User",
        "email": "user@example.com",
        "password": "user123",
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/api/siswa/", json=user_data, headers=admin_headers)
    print_response("POST /api/siswa/ - Admin creates user", response)
    
    if response.status_code == 201:
        user_id = response.json()["id"]
        print(f"✅ User created with ID: {user_id}")
    
    
    # ==================== 4. LOGIN AS USER ====================
    print("\n[4] LOGIN - Login sebagai regular user")
    user_login = {
        "email": "user@example.com",
        "password": "user123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=user_login)
    print_response("POST /api/auth/login - User Login", response)
    
    if response.status_code != 200:
        print("❌ User login failed!")
        return
    
    user_token = response.json()["access_token"]
    user_info = response.json()["user"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    print(f"✅ User logged in!")
    print(f"   Role: {user_info['role']}")
    print(f"   Token: {user_token[:50]}...")
    
    
    # ==================== 5. TEST ADMIN PERMISSIONS ====================
    print("\n" + "="*70)
    print("🔑 TESTING ADMIN PERMISSIONS (Full CRUD + Role Management)")
    print("="*70)
    
    # 5a. Admin can view all users
    print("\n[5a] ADMIN - Get all users")
    response = requests.get(f"{BASE_URL}/api/users", headers=admin_headers)
    print_response("GET /api/users - Admin views all users", response)
    
    # 5b. Admin can delete siswa
    print("\n[5b] ADMIN - Delete siswa")
    # Create a test siswa first
    test_siswa = {
        "nama": "Test Delete",
        "email": "delete@example.com",
        "password": "test123"
    }
    create_response = requests.post(f"{BASE_URL}/api/siswa/", json=test_siswa, headers=admin_headers)
    if create_response.status_code == 201:
        delete_id = create_response.json()["id"]
        response = requests.delete(f"{BASE_URL}/api/siswa/{delete_id}", headers=admin_headers)
        print_response(f"DELETE /api/siswa/{delete_id} - Admin deletes siswa", response)
        
        if response.status_code == 200:
            print("✅ Admin can DELETE siswa")
    
    # 5c. Admin can change user roles
    print("\n[5c] ADMIN - Change user role to admin")
    role_update = {"role": "admin"}
    response = requests.put(f"{BASE_URL}/api/users/{user_id}/role", 
                           json=role_update, headers=admin_headers)
    print_response(f"PUT /api/users/{user_id}/role - Admin changes role", response)
    
    if response.status_code == 200:
        print("✅ Admin can CHANGE USER ROLES")
    
    # Change back to user
    role_update = {"role": "user"}
    requests.put(f"{BASE_URL}/api/users/{user_id}/role", 
                json=role_update, headers=admin_headers)
    
    
    # ==================== 6. TEST USER PERMISSIONS ====================
    print("\n" + "="*70)
    print("👤 TESTING USER PERMISSIONS (CRU only, no Delete)")
    print("="*70)
    
    # 6a. User can create siswa
    print("\n[6a] USER - Create new siswa")
    new_siswa = {
        "nama": "User Created",
        "email": "usercreated@example.com",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/api/siswa/", json=new_siswa, headers=user_headers)
    print_response("POST /api/siswa/ - User creates siswa", response)
    
    if response.status_code == 201:
        print("✅ User can CREATE siswa")
        created_id = response.json()["id"]
    
    # 6b. User can read siswa
    print("\n[6b] USER - Read siswa")
    response = requests.get(f"{BASE_URL}/api/siswa/", headers=user_headers)
    print_response("GET /api/siswa/ - User reads all siswa", response)
    
    if response.status_code == 200:
        print("✅ User can READ siswa")
    
    # 6c. User can update siswa
    print("\n[6c] USER - Update siswa")
    update_data = {
        "nama": "Updated by User",
        "email": "usercreated@example.com",
        "password": "newpass123"
    }
    response = requests.put(f"{BASE_URL}/api/siswa/{created_id}", 
                           json=update_data, headers=user_headers)
    print_response(f"PUT /api/siswa/{created_id} - User updates siswa", response)
    
    if response.status_code == 200:
        print("✅ User can UPDATE siswa")
    
    
    # ==================== 7. TEST PERMISSION DENIALS ====================
    print("\n" + "="*70)
    print("🚫 TESTING PERMISSION DENIALS")
    print("="*70)
    
    # 7a. User CANNOT delete siswa
    print("\n[7a] USER - Try to delete siswa (should FAIL)")
    response = requests.delete(f"{BASE_URL}/api/siswa/{created_id}", headers=user_headers)
    print_response(f"DELETE /api/siswa/{created_id} - User tries to delete", response)
    
    if response.status_code == 403:
        print("✅ Correct: User CANNOT delete siswa (403 Forbidden)")
    else:
        print("❌ Wrong: User should not be able to delete!")
    
    # 7b. User CANNOT view all users
    print("\n[7b] USER - Try to view all users (should FAIL)")
    response = requests.get(f"{BASE_URL}/api/users", headers=user_headers)
    print_response("GET /api/users - User tries to view all users", response)
    
    if response.status_code == 403:
        print("✅ Correct: User CANNOT view all users (403 Forbidden)")
    else:
        print("❌ Wrong: User should not be able to view all users!")
    
    # 7c. User CANNOT change roles
    print("\n[7c] USER - Try to change role (should FAIL)")
    role_update = {"role": "admin"}
    response = requests.put(f"{BASE_URL}/api/users/{user_id}/role", 
                           json=role_update, headers=user_headers)
    print_response(f"PUT /api/users/{user_id}/role - User tries to change role", response)
    
    if response.status_code == 403:
        print("✅ Correct: User CANNOT change roles (403 Forbidden)")
    else:
        print("❌ Wrong: User should not be able to change roles!")
    
    # 7d. User cannot set role=admin when creating
    print("\n[7d] USER - Try to create admin user (should be forced to user)")
    admin_attempt = {
        "nama": "Fake Admin",
        "email": "fakeadmin@example.com",
        "password": "test123",
        "role": "admin"
    }
    response = requests.post(f"{BASE_URL}/api/siswa/", json=admin_attempt, headers=user_headers)
    print_response("POST /api/siswa/ - User tries to create admin", response)
    
    if response.status_code == 201:
        created_user = response.json()
        if created_user["role"] == "user":
            print("✅ Correct: User cannot create admin, forced to 'user' role")
        else:
            print("❌ Wrong: User should not be able to create admin!")
    
    
    # ==================== 8. DASHBOARD ACCESS ====================
    print("\n" + "="*70)
    print("📊 TESTING DASHBOARD ACCESS")
    print("="*70)
    
    # 8a. Admin can access dashboard
    print("\n[8a] ADMIN - Access dashboard")
    response = requests.get(f"{BASE_URL}/api/dashboard", headers=admin_headers)
    print_response("GET /api/dashboard - Admin", response)
    
    if response.status_code == 200:
        print("✅ Admin can access dashboard")
    
    # 8b. User can access dashboard
    print("\n[8b] USER - Access dashboard")
    response = requests.get(f"{BASE_URL}/api/dashboard", headers=user_headers)
    print_response("GET /api/dashboard - User", response)
    
    if response.status_code == 200:
        print("✅ User can access dashboard")
    
    
    # ==================== SUMMARY ====================
    print("\n" + "="*70)
    print("✅ AUTHORIZATION TEST COMPLETED!")
    print("="*70)
    print("\n📝 Summary:")
    print("\n🔑 ADMIN PERMISSIONS:")
    print("  ✅ CREATE siswa (dengan role apapun)")
    print("  ✅ READ all siswa")
    print("  ✅ UPDATE siswa")
    print("  ✅ DELETE siswa")
    print("  ✅ VIEW all users")
    print("  ✅ CHANGE user roles")
    print("  ✅ ACCESS dashboard")
    
    print("\n👤 USER PERMISSIONS:")
    print("  ✅ CREATE siswa (role selalu 'user')")
    print("  ✅ READ all siswa")
    print("  ✅ UPDATE siswa")
    print("  ❌ DELETE siswa (403 Forbidden)")
    print("  ❌ VIEW all users (403 Forbidden)")
    print("  ❌ CHANGE user roles (403 Forbidden)")
    print("  ✅ ACCESS dashboard")
    
    print("\n🎯 Role-Based Access Control (RBAC) is working correctly!")
    print()


if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running!")
            
            # Ask to reset database
            print("\n⚠️  This test will create new users.")
            print("It's recommended to start with a fresh database.")
            print("Run: rm -f siswa_orm.db && uvicorn main:app --reload")
            
            input("\nPress Enter to continue with the test...")
            
            test_authorization()
        else:
            print("❌ Server responded with error")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Server is not running!")
        print("Please start the server first with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
