from PIL import Image
import json
import re

# Read map data from file
with open("map.json.json", "r") as file:
    map_data = json.load(file)["rooms"]

# Define colors for terrain types
terrain_colors = {
    '0': (228, 228, 228),  # white for terrain type 0
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

# Set the chunk size
chunk_size = 5

# Create a blank image for the complete map
complete_map = Image.new('RGB', (width * 50 * 24, height * 50 * 24), (255, 255, 255))

# Iterate through chunks and create corresponding images
for x_chunk in range(0, width * 50, chunk_size * 50):
    for y_chunk in range(0, height * 50, chunk_size * 50):
        # Create an image for the current chunk
        chunk_image = Image.new('RGB', (chunk_size * 50 * 24, chunk_size * 50 * 24), (255, 255, 255))
        chunk_pixels = chunk_image.load()

        for room in map_data:
            room_data = room["terrain"]
            room_objects = room["objects"]

            index_n_s = room["room"].find("N") if "N" in room["room"] else room["room"].find("S")

            room_x = extract_numeric(room["room"][1:index_n_s])
            room_y = extract_numeric(room["room"][index_n_s + 1:])

            current_x = room_x * 50 * 24
            current_y = room_y * 50 * 24

            if room["room"][0] == "E":
                current_x += width * 50 * 24 // 2
            elif room["room"][0] == "W" and current_x != 0:
                current_x = width * 50 * 24 // 2 - current_x - 50 * 24
            elif room["room"][0] == "W" and current_x == 0:
                current_x = width * 50 * 24 // 2 - 50 * 24

            if "S" in room["room"]:
                current_y += height * 50 * 24 // 2
            elif "N" in room["room"] and current_y != 0:
                current_y = height * 50 * 24 // 2 - current_y - 50 * 24
            elif "N" in room["room"] and current_y == 0:
                current_y = height * 50 * 24 // 2 - 50 * 24

            room_width = 50
            room_height = 50

            room_image = Image.new('RGB', (room_width * 24, room_height * 24), (255, 255, 255))
            room_pixels = room_image.load()

            for i in range(len(room_data)):
                x = (i % 50) * 24
                y = (i // 50) * 24
                terrain_type = room_data[i]

                for dx in range(24):
                    for dy in range(24):
                        room_pixels[x + dx, y + dy] = terrain_colors.get(terrain_type, (228, 228, 228))

            for obj in room_objects:
                x = obj.get('x') * 24
                y = obj.get('y') * 24

                for dx in range(24):
                    for dy in range(24):
                        if obj.get('type') == "mineral":
                            room_pixels[x + dx, y + dy] = (255, 192, 203)
                        elif obj.get('type') == "source":
                            room_pixels[x + dx, y + dy] = (255, 255, 0)
                        elif obj.get('type') == "controller":
                            room_pixels[x + dx, y + dy] = (0, 255, 0)
                        elif obj.get('type') == "portal":
                            room_pixels[x + dx, y + dy] = (0, 0, 255)
                        elif obj.get('type') == "keeperLair":
                            room_pixels[x + dx, y + dy] = (255, 0, 0)

            chunk_image.paste(room_image, (current_x - x_chunk, current_y - y_chunk))

        complete_map.paste(chunk_image, (x_chunk, y_chunk))

# Save the final complete map image
complete_map.save("working_scaled_24x_chunked.png")
print("Saving complete scaled map image (24x, aggressive chunking)")
