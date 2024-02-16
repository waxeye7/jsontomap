from PIL import Image, ImageFont, ImageDraw
import json
import re
import time

OPACITY = 0.25  # Constant for opacity value
scale_factor = 4 # Constant for scale factor

# Record the start time
start_time = time.time()

# Read map data from file
with open("shard3.json", "r") as file:
    map_data = json.load(file)["rooms"]

# Read room statuses from file
with open("room_statuses.json", "r") as status_file:
    room_statuses = json.load(status_file)

# Read objects data from file
with open("objects_file.json", "r") as objects_file:
    objects_data = json.load(objects_file)

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
complete_map = Image.new('RGBA', (width * 50 * scale_factor, height * 50 * scale_factor), (255, 255, 255, 255))


# Iterate through each room and create corresponding images
for room in map_data:
    room_data = room["terrain"]
    

    room_status_index = next((index for index, status in enumerate(room_statuses) if status['room_name'] == room['room']), None)
    room_objects_index = next((index for index, obj in enumerate(objects_data) if obj['room_name'] == room['room']), None)




    # Extract status and remove the element from the array
    status = room_statuses[room_status_index]['status'] if room_status_index is not None else None
    objects = objects_data[room_objects_index]['objects'] if room_objects_index is not None else None


    if room_status_index is not None:
        del room_statuses[room_status_index]
    if room_objects_index is not None:
        del objects_data[room_objects_index]

    # Find the index of N or S in the room name
    index_n_s = room["room"].find("N") if "N" in room["room"] else room["room"].find("S")

    # Extract coordinates
    room_x = extract_numeric(room["room"][1:index_n_s])
    room_y = extract_numeric(room["room"][index_n_s + 1:])

    # Calculate the position in the complete map with scale_factor applied
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

    # Ensure the width and height are 50 * scale_factor
    room_width = 50 * scale_factor
    room_height = 50 * scale_factor

    # Create an image for the current room
    room_image = Image.new('RGBA', (room_width, room_height), (255, 255, 255, 255))
    room_draw = ImageDraw.Draw(room_image)

    # Specify the font size (adjust as needed)
    font_size = 20
    font = ImageFont.truetype("arial.ttf", font_size)

    room_pixels = room_image.load()

    # Populate pixels based on map data for the current room
    for i in range(len(room_data)):
        x = (i % 50) * scale_factor
        y = (i // 50) * scale_factor
        terrain_type = room_data[i]

        objects_here = [obj for obj in objects if obj['x'] == i % 50 and obj['y'] == i // 50]

        object_here = next(
            (obj for obj in objects_here if objects_here.count(obj) == 1 or obj.get('type') not in ['rampart', 'creep', 'road', 'powerCreep', 'constructionSite', 'extractor']),
            None
        )

        for dx in range(scale_factor):
            for dy in range(scale_factor):
                if object_here is not None and object_here['type'] != "creep" and object_here['type'] != "powerCreep":
                    if object_here['type'] == "constructedWall":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (0, 0, 0, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (0, 0, 0, 255)
                    elif object_here['type'] == "portal":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 0, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 0, 255, 255)
                    elif object_here['type'] == "keeperLair":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 0, 0, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 0, 0, 255)
                    elif object_here['type'] == "source":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 0, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 0, 255)
                    elif object_here['type'] == "mineral":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 192, 203, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 192, 203, 255)
                    elif object_here['type'] == "controller":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (0, 255, 0, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (0, 255, 0, 255)
                    elif object_here['type'] == "powerBank":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "powerSpawn":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "extractor":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "lab":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "terminal":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "tower":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "observer":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "nuker":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "factory":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    elif object_here['type'] == "invaderCore":
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (255, 255, 255, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (255, 255, 255, 255)
                    else:
                        if status == "out of borders":
                            # If status is "closed", set opacity to the constant value
                            room_pixels[x + dx, y + dy] = (0, 0, 0, int(255 * OPACITY))
                        else:
                            room_pixels[x + dx, y + dy] = (0, 0, 0, 255)
                else:
                    adj_x = x + dx
                    adj_y = y + dy
                    # Check if the coordinates are within the valid range
                    if(adj_y < 0 or adj_x < 0 or adj_y >= 50 * scale_factor or adj_x >= 50 * scale_factor):
                        continue
                    # Fill pixels for terrain type with adjusted opacity
                    if status == "out of borders":
                        # If status is "closed", set opacity to the constant value
                        room_pixels[adj_x, adj_y] = (*terrain_colors.get(terrain_type, (255, 255, 255)), int(255 * OPACITY))
                    else:
                        # Otherwise, use full opacity
                        room_pixels[adj_x, adj_y] = (*terrain_colors.get(terrain_type, (255, 255, 255)), 255)

        if object_here:

            
            letter = ""

            if object_here['type'] == "spawn":
                letter = "S"
            elif object_here['type'] == "extension":
                letter = "E"
            elif object_here['type'] == "tower":
                letter = "T"
            elif object_here['type'] == "storage":
                letter = "O"
            elif object_here['type'] == "lab":
                letter = "L"
            elif object_here['type'] == "terminal":
                letter = "R"
            elif object_here['type'] == "extractor":
                letter = "X"
            elif object_here['type'] == "factory":
                letter = "F"
            elif object_here['type'] == "observer":
                letter = "V"
            elif object_here['type'] == "powerSpawn":
                letter = "P"
            elif object_here['type'] == "nuker":
                letter = "N"
            elif object_here['type'] == "powerBank":
                letter = "B"
            elif object_here['type'] == "controller":
                letter = "C"
            elif object_here['type'] == "link":
                letter = "K"
            elif object_here['type'] == "rampart":
                letter = "M"
            elif object_here['type'] == "portal":
                letter = "U"
            elif object_here['type'] == "constructedWall":
                letter = "W"
            elif object_here['type'] == "road":
                letter = "A"
            elif object_here['type'] == "source":
                letter = "S"
            elif object_here['type'] == "mineral":
                letter = "M"
            elif object_here['type'] == "sourceKeeperLair":
                letter = "K"
            elif object_here['type'] == "invaderCore":
                letter = "I"
            elif object_here['type'] == "deposit":
                letter = "D"

            if len(letter) > 0:
                center_x = current_x + x + (room_width // 2)
                center_y = current_y + y + (room_height // 2)
                room_draw.text((center_x - scale_factor // 2, center_y - scale_factor // 2), letter, fill=(255, 255, 255, 255), font=font)

    # Paste the current room image onto the complete map at the correct position
    complete_map.paste(room_image, (current_x, current_y))

    # Logging for each room
    print(f"Processed room {room['room']} successfully.")

mapName = f'shard3x{scale_factor}'
# Save the final complete map image
complete_map.save(f'{mapName}.png')

# Record the end time
end_time = time.time()

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
print(f"Saving complete scaled map image - mapName: {mapName}")
