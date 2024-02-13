from PIL import Image
import json
import re
import time

scale_factor = 1

# Record the start time
start_time = time.time()

# Read map data from file
with open("shard3.json", "r") as file:
    map_data = json.load(file)["rooms"]

# Define colors for terrain types
terrain_colors = {
    '0': (255, 255, 255),  # white for terrain type 0
    '1': (75, 75, 75),      # black for terrain type 1
    # Add more colors for other terrain types as needed
}

# Extract numeric parts of coordinates using regular expressions
extract_numeric = lambda s: int(re.search(r'\d+', s).group()) if re.search(r'\d+', s) else 0

# Initialize variables for max extents
east_max, west_max, north_max, south_max = 0, 0, 0, 0

# Iterate through each room and update max extents
for room in map_data:
    east_max = max(east_max, extract_numeric(room["room"][1:]) if room["room"][0] == "E" else 0)
    west_max = max(west_max, extract_numeric(room["room"][1:]) if room["room"][0] == "W" else 0)

    # Find the index of N or S in the room name
    index_n_s = room["room"].find("N") if "N" in room["room"] else room["room"].find("S")
    north_max = max(north_max, extract_numeric(room["room"][index_n_s + 1:]) if "N" in room["room"] else 0)
    south_max = max(south_max, extract_numeric(room["room"][index_n_s + 1:]) if "S" in room["room"] else 0)

# Calculate the width and height of the complete map image
width = (east_max + west_max) + 2
height = (north_max + south_max) + 2

# Create a blank image for the complete map
complete_map = Image.new('RGB', (width * 50 * scale_factor, height * 50 * scale_factor), (255, 255, 255))

# Iterate through each room and create corresponding images
for room in map_data:
    room_data = room["terrain"]
    room_objects = room["objects"]
    status = room["status"] if "status" in room else None

    # Find the index of N or S in the room name
    index_n_s = room["room"].find("N") if "N" in room["room"] else room["room"].find("S")

    # Extract coordinates
    room_x = extract_numeric(room["room"][1:index_n_s])
    room_y = extract_numeric(room["room"][index_n_s + 1:])

    # Calculate the position in the complete map
    current_x = room_x * 50 * scale_factor
    current_y = room_y * 50 * scale_factor

    # Adjust offsets based on room direction
    if room["room"][0] == "E":
        current_x += width * 50 * scale_factor // 2  # Shift right for east rooms
    elif room["room"][0] == "W" and current_x != 0:
        current_x = width * 50 * scale_factor // 2 - current_x - 50 * scale_factor  # Shift left for west rooms
    elif room["room"][0] == "W" and current_x == 0:
        current_x = width * 50 * scale_factor // 2 - 50 * scale_factor

    if "S" in room["room"]:
        current_y += height * 50 * scale_factor // 2  # Shift down for south rooms
    elif "N" in room["room"] and current_y != 0:
        current_y = height * 50 * scale_factor // 2 - current_y - 50 * scale_factor  # Shift up for north rooms
    elif "N" in room["room"] and current_y == 0:
        current_y = height * 50 * scale_factor // 2 - 50 * scale_factor

    # Ensure the width and height are 50
    room_width = 50
    room_height = 50

    # Create an image for the current room
    room_image = Image.new('RGB', (room_width * scale_factor, room_height * scale_factor), (255, 255, 255))
    room_pixels = room_image.load()

    # Populate pixels based on map data for the current room
    for i in range(len(room_data)):
        x = (i % 50) * scale_factor
        y = (i // 50) * scale_factor
        terrain_type = room_data[i]

        # Fill pixels for terrain type
        for dx in range(scale_factor):
            for dy in range(scale_factor):
                if status == "normal":
                    # If status is "normal", make the color white
                    room_pixels[x + dx, y + dy] = terrain_colors.get(terrain_type, (255, 255, 255))
                else:
                    # Otherwise, use dark gray color
                    room_pixels[x + dx, y + dy] = (50, 50, 50)

    for obj in room_objects:
        x = obj.get('x') * scale_factor if 'x' in obj else 0
        y = obj.get('y') * scale_factor if 'y' in obj else 0

        # Fill pixels for objects
        for dx in range(scale_factor):
            for dy in range(scale_factor):
                if obj.get('type') == "mineral":
                    room_pixels[x + dx, y + dy] = (255, 192, 203)
                elif obj.get('type') == "source":
                    room_pixels[x + dx, y + dy] = (255, 255, 0)
                elif obj.get('type') == "controller":
                    room_pixels[x + dx, y + dy] = (0, 255, 0)
                elif obj.get('type') == "keeperLair":
                    room_pixels[x + dx, y + dy] = (255, 0, 0)

    # Paste the current room image onto the complete map at the correct position
    complete_map.paste(room_image, (current_x, current_y))

    # Logging for each room
    print(f"Processed room {room['room']} successfully.")

# Save the final complete map image
complete_map.save("shard3x4.png")

# Record the end time
end_time = time.time()

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
print("Saving complete scaled map image (1x)")
