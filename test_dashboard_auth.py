"""Test script for JARVIS dashboard authentication."""

import requests
import time


def test_dashboard_auth():
    """Test the dashboard authentication endpoints."""
    base_url = "http://localhost:3000"
    
    print("Testing JARVIS Dashboard Authentication")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print(f"✓ Health check passed: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running?")
        print("  Start with: python -m jarvis.dashboard")
        return
    
    # Test 2: Login with valid credentials
    print("\n2. Testing login with valid credentials...")
    response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin",
        "password": "jarvis123"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✓ Login successful")
        print(f"  User ID: {data.get('user_id')}")
        print(f"  Token expires in: {data.get('expires_in')} seconds")
        print(f"  Token (first 50 chars): {token[:50]}...")
    else:
        print(f"✗ Login failed: {response.status_code} - {response.json()}")
        return
    
    # Test 3: Access protected endpoint with token
    print("\n3. Testing protected endpoint with valid token...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/api/protected", headers=headers)
    
    if response.status_code == 200:
        print(f"✓ Protected endpoint access granted: {response.json()}")
    else:
        print(f"✗ Protected endpoint access denied: {response.status_code}")
    
    # Test 4: Verify token
    print("\n4. Testing token verification...")
    response = requests.get(f"{base_url}/api/auth/verify", headers=headers)
    
    if response.status_code == 200:
        print(f"✓ Token verification passed: {response.json()}")
    else:
        print(f"✗ Token verification failed: {response.status_code}")
    
    # Test 5: Access protected endpoint without token
    print("\n5. Testing protected endpoint without token...")
    response = requests.get(f"{base_url}/api/protected")
    
    if response.status_code == 401:
        print(f"✓ Correctly rejected unauthorized access: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    # Test 6: Login with invalid credentials
    print("\n6. Testing login with invalid credentials...")
    response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    
    if response.status_code == 401:
        print(f"✓ Correctly rejected invalid credentials: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    # Test 7: Login with missing fields
    print("\n7. Testing login with missing fields...")
    response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin"
    })
    
    if response.status_code == 400:
        print(f"✓ Correctly rejected missing password: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    # Test 8: Access with invalid token
    print("\n8. Testing protected endpoint with invalid token...")
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(f"{base_url}/api/protected", headers=headers)
    
    if response.status_code == 401:
        print(f"✓ Correctly rejected invalid token: {response.json()}")
    else:
        print(f"✗ Should have rejected but got: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    test_dashboard_auth()
