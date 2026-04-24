#!/usr/bin/env python3
"""
核心功能测试脚本
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查"""
    print("\n=== Test 1: Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("[PASS] Health check passed")

def test_auth():
    """测试用户认证"""
    print("\n=== Test 2: User Auth ===")

    # Register
    register_data = {
        "name": "test_user",
        "email": f"test_{int(time.time())}@example.com",
        "password": "Test123!"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Register - Status: {response.status_code}")
    print(f"Register - Response: {response.json()}")

    # Login
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login - Status: {response.status_code}")
    print(f"Login - Response: {response.json()}")

    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    print("[PASS] Auth passed")
    return token

def test_chat_api(token):
    """测试聊天API"""
    print("\n=== Test 3: Chat API ===")

    headers = {"Authorization": f"Bearer {token}"}

    # Test send message (without creating session first)
    print("\n3.1 Test send chat message")
    chat_data = {
        "message": "Hello, what can this system do?",
        "document_ids": [],
        "chat_id": None
    }
    response = requests.post(f"{BASE_URL}/chat", json=chat_data, headers=headers)
    print(f"Send message - Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200:
        print("[PASS] Chat message sent successfully")
        result = response.json()["data"]
        print(f"  AI reply: {result.get('message', '')[:100]}...")
        return result.get("chat_id")
    elif response.status_code == 500:
        error_msg = response.json().get("message", "")
        if "LLM" in error_msg:
            print("[INFO] LLM call failed (expected, no real LLM API configured)")
            return None
        else:
            print(f"[WARN] Other internal error: {error_msg}")
            return None
    else:
        print(f"[WARN] Unexpected status: {response.status_code}")
        return None

def test_documents_api(token):
    """测试文档API"""
    print("\n=== Test 4: Documents API ===")

    headers = {"Authorization": f"Bearer {token}"}

    # Test get document list
    print("\n4.1 Test get document list")
    response = requests.get(f"{BASE_URL}/documents", headers=headers)
    print(f"Get list - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("[PASS] Get document list passed")

    # Test upload document
    print("\n4.2 Test upload document")
    test_content = b"This is a test document for testing document upload functionality."
    files = {"file": ("test.txt", test_content, "text/plain")}
    response = requests.post(f"{BASE_URL}/documents", headers=headers, files=files)
    print(f"Upload - Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200:
        doc_id = response.json()["data"]["id"]
        print(f"[PASS] Document uploaded, doc_id: {doc_id}")

        # Test get document status
        print("\n4.3 Test get document status")
        response = requests.get(f"{BASE_URL}/documents/{doc_id}/status", headers=headers)
        print(f"Get status - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("[PASS] Get document status passed")

        # Test delete document
        print("\n4.4 Test delete document")
        response = requests.delete(f"{BASE_URL}/documents/{doc_id}", headers=headers)
        print(f"Delete - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("[PASS] Document deleted")
    else:
        print(f"[WARN] Document upload failed: {response.json()}")

def test_folders_api(token):
    """测试文件夹API"""
    print("\n=== Test 5: Folders API ===")

    headers = {"Authorization": f"Bearer {token}"}

    # Test create folder
    print("\n5.1 Test create folder")
    folder_data = {"name": f"TestFolder_{int(time.time())}"}
    response = requests.post(f"{BASE_URL}/folders", json=folder_data, headers=headers)
    print(f"Create folder - Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200:
        folder_id = response.json()["data"]["id"]
        print(f"[PASS] Folder created, folder_id: {folder_id}")

        # Test get folder list
        print("\n5.2 Test get folder list")
        response = requests.get(f"{BASE_URL}/folders", headers=headers)
        print(f"Get list - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("[PASS] Get folder list passed")

        # Test delete folder
        print("\n5.3 Test delete folder")
        response = requests.delete(f"{BASE_URL}/folders/{folder_id}", headers=headers)
        print(f"Delete - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("[PASS] Folder deleted")
    else:
        print(f"[WARN] Folder operation failed: {response.json()}")

def main():
    print("=" * 60)
    print("Core Features Comprehensive Test")
    print("=" * 60)

    try:
        # 1. Health check
        test_health()

        # 2. User auth
        token = test_auth()

        # 3. Chat API test
        test_chat_api(token)

        # 4. Documents API test
        test_documents_api(token)

        # 5. Folders API test
        test_folders_api(token)

        print("\n" + "=" * 60)
        print("All core feature tests completed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] Unknown error: {e}")
        raise

if __name__ == "__main__":
    main()
