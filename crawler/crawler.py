import requests
url = "https://edge01.155626.ir.cdn.ir/aG5p/Film/New-Server/"

response = requests.get(url, timeout=30)

print(f"Status Code: {response.status_code}")
print(response.text[:1000])
