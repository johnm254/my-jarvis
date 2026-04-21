"""Test script for JARVIS dashboard memory API endpoints."""

import requests


def test_memory_api():
    """Test the dashboard memory API endpoints."""
    base_url = "http://localhost:3000"
    
    print("Testing JARVIS Dashboard Memory API")
    print("=" * 50)
    
    # First, login to get a token
    print("\n0. Logging in to get authentication token...")
    response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin",
        "password": "jarvis123"
    })
    
    if response.status_code != 200:
        print(f"✗ Login failed: {response.status_code}")
        print("  Make sure the server is running: python -m jarvis.dashboard")
        return
    
    token = response.json().get('token')
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ Login successful, token obtained")
    
    # Test 1: Search memories
    print("\n1. Testing GET /api/memory/search...")
    response = requests.get(
        f"{base_url}/api/memory/search",
        headers=headers,
        params={"query": "weather", "limit": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Memory search successful")
        print(f"  Query: {data.get('query')}")
        print(f"  Results count: {data.get('count')}")
        if data.get('results'):
            print(f"  First result: {data['results'][0].get('user_input', 'N/A')[:50]}...")
    else:
        print(f"✗ Memory search failed: {response.status_code} - {response.json()}")
    
    # Test 2: Search without query parameter
    print("\n2. Testing search without query parameter...")
    response = requests.get(
        f"{base_url}/api/memory/search",
        headers=headers
    )
    
    if response.status_code == 400:
        print(f"✓ Correctly rejected missing query: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    # Test 3: Update user preference
    print("\n3. Testing PUT /api/memory/update (single preference)...")
    response = requests.put(
        f"{base_url}/api/memory/update",
        headers=headers,
        json={
            "preference_key": "favorite_color",
            "preference_value": "blue"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Preference update successful")
        print(f"  Message: {data.get('message')}")
        print(f"  User ID: {data.get('user_id')}")
    else:
        print(f"✗ Preference update failed: {response.status_code} - {response.json()}")
    
    # Test 4: Update profile fields
    print("\n4. Testing PUT /api/memory/update (profile updates)...")
    response = requests.put(
        f"{base_url}/api/memory/update",
        headers=headers,
        json={
            "profile_updates": {
                "first_name": "TestUser",
                "timezone": "America/Los_Angeles",
                "communication_style": "technical"
            }
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Profile update successful")
        print(f"  Message: {data.get('message')}")
        print(f"  Updated fields: {data.get('updated_fields')}")
    else:
        print(f"✗ Profile update failed: {response.status_code} - {response.json()}")
    
    # Test 5: Update without required fields
    print("\n5. Testing update without required fields...")
    response = requests.put(
        f"{base_url}/api/memory/update",
        headers=headers,
        json={}
    )
    
    if response.status_code == 400:
        print(f"✓ Correctly rejected empty update: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    # Test 6: Delete specific conversation (if exists)
    print("\n6. Testing DELETE /api/memory/delete (specific conversation)...")
    # Using a fake UUID for testing
    response = requests.delete(
        f"{base_url}/api/memory/delete",
        headers=headers,
        json={
            "conversation_id": "00000000-0000-0000-0000-000000000001"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Delete request processed")
        print(f"  Message: {data.get('message')}")
        print(f"  Deleted count: {data.get('deleted_count')}")
    else:
        print(f"✗ Delete failed: {response.status_code} - {response.json()}")
    
    # Test 7: Delete by session_id
    print("\n7. Testing DELETE /api/memory/delete (by session)...")
    response = requests.delete(
        f"{base_url}/api/memory/delete",
        headers=headers,
        json={
            "session_id": "test_session_123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Session delete request processed")
        print(f"  Message: {data.get('message')}")
        print(f"  Deleted count: {data.get('deleted_count')}")
    else:
        print(f"✗ Session delete failed: {response.status_code} - {response.json()}")
    
    # Test 8: Delete all without confirmation
    print("\n8. Testing DELETE /api/memory/delete (all without confirmation)...")
    response = requests.delete(
        f"{base_url}/api/memory/delete",
        headers=headers,
        json={
            "delete_all": True
        }
    )
    
    if response.status_code == 403:
        print(f"✓ Correctly rejected bulk delete without confirmation: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    # Test 9: Delete without parameters
    print("\n9. Testing delete without parameters...")
    response = requests.delete(
        f"{base_url}/api/memory/delete",
        headers=headers,
        json={}
    )
    
    if response.status_code == 400:
        print(f"✓ Correctly rejected empty delete request: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    # Test 10: Access memory endpoints without authentication
    print("\n10. Testing memory endpoints without authentication...")
    response = requests.get(f"{base_url}/api/memory/search?query=test")
    
    if response.status_code == 401:
        print(f"✓ Correctly rejected unauthorized access: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("All memory API tests completed!")


if __name__ == "__main__":
    test_memory_api()
