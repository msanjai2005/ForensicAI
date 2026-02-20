import sys
sys.path.insert(0, '.')

try:
    print("Testing imports...")
    from database import init_database, get_connection
    print("[OK] Database module")
    
    from engines.case_management import CaseManagementEngine
    print("[OK] Case management")
    
    from engines.ingestion import IngestionEngine
    print("[OK] Ingestion engine")
    
    print("\nInitializing database...")
    init_database()
    print("[OK] Database initialized")
    
    print("\nTesting case creation...")
    case_id = CaseManagementEngine.create_case("Test Case", "Test Description")
    print(f"[OK] Case created: {case_id}")
    
    print("\nTesting file ingestion...")
    test_content = b"timestamp,type,user_id\n2024-01-01,login,user1"
    upload_id, result = IngestionEngine.ingest_file(case_id, "test.csv", test_content)
    if upload_id:
        print(f"[OK] File ingested: {upload_id}")
    else:
        print(f"[FAIL] Ingestion failed: {result}")
    
    print("\n[OK] All tests passed!")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
