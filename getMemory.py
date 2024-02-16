import os
import base64
import zlib
import json
import requests
import gzip
from dotenv import load_dotenv
load_dotenv()
# Get the Screeps authentication token and shard from the environment
auth_token = os.getenv("SCREEPS_AUTH_TOKEN")
shard_name = "shard3"  # Add SCREEPS_SHARD_NAME to your .env file

# Check if the token and shard are available
if not auth_token:
    raise ValueError("SCREEPS_AUTH_TOKEN is not set in the .env file")
if not shard_name:
    raise ValueError("SCREEPS_SHARD_NAME is not set in the .env file")

# Screeps API endpoint for getting Memory data
api_url = f"https://screeps.com/api/user/memory?shard={shard_name}"

# Build the request URL
url = f"{api_url}&_token={auth_token}"

# Make the GET request to the Screeps API
response = requests.get(url)

# Check if the request was successful (HTTP status code 200)
if response.status_code == 200:
    # Decode base64
    base64_data = response.json()["data"]
    decoded_data = base64.b64decode(base64_data)
    
    try:
        # Try to parse the data as JSON
        data = json.loads(decoded_data.decode("utf-8"))
        print("Room Statuses:", data.get("roomStatuses", []))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
else:
    print(f"Error: Unable to fetch data. HTTP Status Code: {response.status_code}")
    print("Response:", response.text)