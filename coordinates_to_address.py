def coordinates_to_address(lat, lon):
    # Connect to the database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Retrieve addresses within a +/- 0.001 degree range of the original coordinates
    cursor.execute('''
        SELECT id, lat, lon, tags
        FROM nodes
        WHERE lat >= ? AND lat <= ? AND lon >= ? AND lon <= ?
    ''', (lat - 0.001, lat + 0.001, lon - 0.001, lon + 0.001))
    rows = cursor.fetchall()
    if len(rows) == 0:
        conn.close()  # Close the connection before returning
        return None

    # Find the address with the smallest distance from the original coordinates
    min_distance = float('inf')
    closest_address = None
    for row in rows:
        id, node_lat, node_lon, tags = row
        distance = math.sqrt((node_lat - lat) ** 2 + (node_lon - lon) ** 2)
        if distance < min_distance:
            if tags.count('addr:') > 2:
                min_distance = distance
                closest_address = {'id': id, 'lat': node_lat, 'lon': node_lon, 'tags': tags}

    # Parse the tags column to find the address
    #address = {}
    #for tag in closest_address['tags'].split(','):
    #    k, v = tag.split(':', 1)
    #    address[k] = v

    # Close the connection to the database
    conn.close()

    # Return the address
    return closest_address
