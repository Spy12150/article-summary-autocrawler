import requests
import json
import time
import sys

"""Test connection to the LLM endpoint to debug connectivity issues"""

def test_endpoint_connection(endpoint="http://10.30.15.111:8080/v1/chat/completions"):
    """Test basic connectivity to the endpoint"""
    print(f"🔍 Testing connection to: {endpoint}")
    print("-" * 50)
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(endpoint.replace('/v1/chat/completions', ''), timeout=5)
        print(f"✅ Base URL is reachable (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Base URL not reachable: {e}")
        return False
    
    # Test 2: Try the actual endpoint
    headers = {
        "Authorization": "Bearer test_key",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "Deepseek-r1:32b",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=10
        )
        print(f"✅ Endpoint responds (status: {response.status_code})")
        
        if response.status_code == 401:
            print("ℹ️  Authentication required (expected)")
        elif response.status_code == 200:
            print("✅ Endpoint working correctly")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False
    
    return True

def test_alternative_endpoints():
    """Test alternative endpoints that might work"""
    print("\n🔄 Testing alternative endpoints...")
    print("-" * 50)
    
    alternatives = [
        "http://localhost:8080/v1/chat/completions",
        "http://127.0.0.1:8080/v1/chat/completions",
        "https://10.30.15.111:8080/v1/chat/completions",
    ]
    
    for endpoint in alternatives:
        print(f"\nTesting: {endpoint}")
        try:
            response = requests.get(endpoint.replace('/v1/chat/completions', ''), timeout=3)
            print(f"✅ {endpoint} is reachable")
        except Exception as e:
            print(f"❌ {endpoint} failed: {e}")

def create_mock_endpoint_test():
    """Create a test that simulates successful processing"""
    print("\n🧪 Creating mock test...")
    print("-" * 50)
    
    # Simulate what a successful response would look like
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": '{"sentiment": "positive", "summary": "Test summary for mock processing"}'
                }
            }
        ]
    }
    
    try:
        content = mock_response['choices'][0]['message']['content']
        result = json.loads(content)
        print(f"✅ Mock response parsing works:")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Summary: {result['summary']}")
        return True
    except Exception as e:
        print(f"❌ Mock response parsing failed: {e}")
        return False

def main():
    """Run all connection tests"""
    print("🚀 LLM Endpoint Connection Tester")
    print("=" * 60)
    
    # Test main endpoint
    endpoint_works = test_endpoint_connection()
    
    # Test alternatives
    test_alternative_endpoints()
    
    # Test mock processing
    mock_works = create_mock_endpoint_test()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print("=" * 60)
    
    if endpoint_works:
        print("✅ Main endpoint is accessible")
        print("💡 The connection issues might be due to:")
        print("   - API key authentication")
        print("   - Rate limiting")
        print("   - Server overload")
        print("   - Network firewall rules")
    else:
        print("❌ Main endpoint is not accessible")
        print("💡 Possible solutions:")
        print("   - Check if you're on the correct network")
        print("   - Verify the IP address (10.30.15.111)")
        print("   - Check if VPN is required")
        print("   - Try the mock mode for testing")
    
    print("\n🛠️  To run with mock mode (for testing):")
    print("   python process_articles.py --endpoint 'mock' --input data/article_data9.json")

if __name__ == "__main__":
    main()
