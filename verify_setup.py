#!/usr/bin/env python
"""
Verification script to ensure clean architecture setup is complete
"""

import sys
import os
from pathlib import Path

def check_files_exist():
    """Check if all required files exist"""
    required_files = [
        'main.py',
        'app/__init__.py',
        'app/database.py',
        'app/models.py',
        'app/api/__init__.py',
        'app/api/v1/__init__.py',
        'app/api/v1/api.py',
        'app/api/v1/endpoints/__init__.py',
        'app/api/v1/endpoints/halo.py',
        'app/api/v1/endpoints/siswa.py',
        'tests/conftest.py',
        'tests/test_main.py',
    ]
    
    print("📁 Checking required files...")
    all_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_imports():
    """Check if all imports work"""
    print("\n📦 Checking imports...")
    try:
        from main import app
        print("  ✅ main.app imports successfully")
    except Exception as e:
        print(f"  ❌ Failed to import main.app: {e}")
        return False
    
    try:
        from app.database import init_db, count_siswa
        print("  ✅ app.database imports successfully")
    except Exception as e:
        print(f"  ❌ Failed to import app.database: {e}")
        return False
    
    try:
        from app.models import SiswaCreate, SiswaUpdate, SiswaResponse
        print("  ✅ app.models imports successfully")
    except Exception as e:
        print(f"  ❌ Failed to import app.models: {e}")
        return False
    
    try:
        from app.api.v1.endpoints.halo import router as halo_router
        print("  ✅ app.api.v1.endpoints.halo imports successfully")
    except Exception as e:
        print(f"  ❌ Failed to import halo router: {e}")
        return False
    
    try:
        from app.api.v1.endpoints.siswa import router as siswa_router
        print("  ✅ app.api.v1.endpoints.siswa imports successfully")
    except Exception as e:
        print(f"  ❌ Failed to import siswa router: {e}")
        return False
    
    try:
        from app.api.v1.api import api_router
        print("  ✅ app.api.v1.api imports successfully")
    except Exception as e:
        print(f"  ❌ Failed to import api router: {e}")
        return False
    
    return True

def check_documentation():
    """Check if documentation files exist"""
    print("\n📚 Checking documentation...")
    docs = ['ARCHITECTURE.md', 'QUICK_START.md', 'MIGRATION_REPORT.md']
    all_exist = True
    for doc in docs:
        exists = os.path.exists(doc)
        status = "✅" if exists else "❌"
        print(f"  {status} {doc}")
        if not exists:
            all_exist = False
    return all_exist

def main():
    print("=" * 60)
    print("🔍 Clean Architecture Setup Verification")
    print("=" * 60)
    
    files_ok = check_files_exist()
    imports_ok = check_imports()
    docs_ok = check_documentation()
    
    print("\n" + "=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)
    print(f"  Files:           {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"  Imports:         {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  Documentation:   {'✅ PASS' if docs_ok else '❌ FAIL'}")
    
    if files_ok and imports_ok and docs_ok:
        print("\n✨ Clean Architecture Setup: COMPLETE ✨")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
