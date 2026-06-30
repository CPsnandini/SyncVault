import requests
import io

BASE = "http://127.0.0.1:5001"

r = requests.post(f"{BASE}/auth/signup", json={"username": "filetest", "password": "testpass123"})
print("SIGNUP:", r.status_code, r.json())

r = requests.post(f"{BASE}/auth/login", json={"username": "filetest", "password": "testpass123"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Upload version 1
file_v1 = io.BytesIO(b"This is version one of the file.")
r = requests.post(f"{BASE}/files/upload", headers=headers, files={"file": ("notes.txt", file_v1)})
print("UPLOAD V1:", r.status_code, r.json())
file_id = r.json()["file_id"]

# Upload version 2 of the SAME filename
file_v2 = io.BytesIO(b"This is version TWO, with more content added.")
r = requests.post(f"{BASE}/files/upload", headers=headers, files={"file": ("notes.txt", file_v2)})
print("UPLOAD V2:", r.status_code, r.json())

# List files
r = requests.get(f"{BASE}/files", headers=headers)
print("LIST FILES:", r.status_code, r.json())

# List versions
r = requests.get(f"{BASE}/files/{file_id}/versions", headers=headers)
print("LIST VERSIONS:", r.status_code, r.json())

# Download latest (should be version 2's content)
r = requests.get(f"{BASE}/files/{file_id}/download", headers=headers)
print("DOWNLOAD LATEST:", r.status_code, r.content)

# Download version 1 specifically
r = requests.get(f"{BASE}/files/{file_id}/download?version=1", headers=headers)
print("DOWNLOAD V1:", r.status_code, r.content)