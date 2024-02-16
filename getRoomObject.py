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

# API endpoint for room objects
room_objects_url = 'https://screeps.com/api/game/room-objects'

# Set headers with the authentication token
headers = {'X-Token': token, 'X-Username': ''}

# Get the world size
world_size = 61

# Function to get room objects for a given room
def get_room_objects(room_name):
    try:
        room_objects_response = requests.get(room_objects_url, params={'room': room_name, 'shard': 'shard3'}, headers=headers)
        room_objects_data = room_objects_response.json()
        if room_objects_data.get('ok'):
            room_objects = room_objects_data['objects']
            print(f"Room: {room_name}, Objects Count: {len(room_objects)}")
            return {'room_name': room_name, 'objects': room_objects}
        else:
            print(f"Failed to retrieve room objects for {room_name}")
            return {'room_name': room_name, 'objects': []}
    except Exception as e:
        print(f"Error for {room_name}: {e}")
        return {'room_name': room_name, 'objects': []}

# Increase the number of workers for concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for x in range(world_size):
        for y in range(world_size):
            for horizontal_direction in ['E', 'W']:
                for vertical_direction in ['N', 'S']:
                    room_name = f"{horizontal_direction}{x}{vertical_direction}{y}"
                    futures.append(executor.submit(get_room_objects, room_name))
                    time.sleep(0.25)

    # Wait for all requests to complete
    results = [future.result() for future in futures]

# Write results to a JSON file
with open('shard3RoomObjects.json', 'w') as json_file:
    json.dump(results, json_file, indent=2)

print("Results saved to shard3RoomObjects.json")
