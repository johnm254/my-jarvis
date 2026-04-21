"""Demo script for JARVIS Dashboard Backend with JWT Authentication."""

import requests
import json


def main():
    """Demonstrate the JARVIS dashboard backend functionality."""
    print("=" * 60)
    print("JARVIS Dashboard Backend Demo")
    print("=" * 60)
    
    base_url = "http://localhost:3000"
    
    print("\n📋 Step 1: Check server health")
    print("-" * 60)
    response = requests.get(f"{base_url}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n🔐 Step 2: Login with credentials")
    print("-" * 60)
    print("Credentials: admin / jarvis123")
    response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin",
        "password": "jarvis123"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    token = data['token']
    print(f"\n✓ JWT Token received (expires in {data['expires_in']} seconds)")
    
    print("\n🔒 Step 3: Access protected endpoint with token")
    print("-" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/api/protected", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n✅ Step 4: Verify token is valid")
    print("-" * 60)
    response = requests.get(f"{base_url}/api/auth/verify", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n❌ Step 5: Try accessing without token (should fail)")
    print("-" * 60)
    response = requests.get(f"{base_url}/api/protected")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    
    print("\n📚 Next Steps:")
    print("  1. Add more protected endpoints for conversation, memory, etc.")
    print("  2. Implement user database with hashed passwords")
    print("  3. Build React frontend to consume these APIs")
    print("  4. Add WebSocket support for real-time updates")
    print("  5. Implement token refresh mechanism")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print("Please start the server first:")
        print("  python -m jarvis.dashboard")
