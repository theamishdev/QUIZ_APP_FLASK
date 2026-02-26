import requests
import json

def test_chat(message):
    url = "http://127.0.0.1:5000/chat"
    headers = {"Content-Type": "application/json"}
    data = {"message": message}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json().get('reply')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Mock Mode...")
    test_chat("Hello, can you list my classrooms?")
    print("-" * 20)
    test_chat("How do I create a quiz?")
