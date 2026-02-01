import requests

API_KEY = "AIzaSyB58WKamRSt2v_S1EXDGz3i3hUcYs2fydQ"
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
headers = {"Content-Type": "application/json"}
data = {"contents": [{"parts": [{"text": "Hello, world!"}]}]}

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
except Exception as e:
    import traceback
    print("Exception occurred:", str(e))
    print(traceback.format_exc())
