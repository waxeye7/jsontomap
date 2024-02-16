import os
from dotenv import load_dotenv
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import time

# Load environment variables from .env
load_dotenv()

# Get the Screeps token from the environment variables
token = os.getenv('SCREEPS_TOKEN')

# Check if the token is available
if not token:
    print('Screeps token not found in the .env file.')
    exit()

# API endpoint for room status
room_status_url = 'https://screeps.com/api/game/room-status'

# Set headers with the authentication token
headers = {'X-Token': token, 'X-Username': ''}

# Get the world size
world_size = 61

# Function to get room status for a given room
def get_room_status(room_name):
    try:
        room_status_response = requests.get(room_status_url, params={'room': room_name, 'shard': 'shard3'}, headers=headers)
        room_status_data = room_status_response.json()
        if room_status_data.get('ok') and room_status_data.get('room'):
            room_info = room_status_data['room']
            status = room_info.get('status')
            print(f"Room: {room_name}, Status: {status}")
            return {'room_name': room_name, 'status': status}
        else:
            print(f"Failed to retrieve room status for {room_name}")
            return {'room_name': room_name, 'status': None}
    except Exception as e:
        print(f"Error for {room_name}: {e}")
        return {'room_name': room_name, 'status': None}

# Increase the number of workers for concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for x in range(world_size):
        for y in range(world_size):
            for horizontal_direction in ['E', 'W']:
                for vertical_direction in ['N', 'S']:
                    room_name = f"{horizontal_direction}{x}{vertical_direction}{y}"
                    futures.append(executor.submit(get_room_status, room_name))
                    time.sleep(0.25)

    # Wait for all requests to complete
    results = [future.result() for future in futures]

# Write results to a JSON file
with open('room_statuses.json', 'w') as json_file:
    json.dump(results, json_file, indent=2)
