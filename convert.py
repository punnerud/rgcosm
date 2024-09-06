import os
import osmium
import sqlite3
import time
import subprocess

class OsmHandler(osmium.SimpleHandler):
    def __init__(self, total_nodes, total_ways):
        osmium.SimpleHandler.__init__(self)
        self.conn = sqlite3.connect('osm.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('PRAGMA synchronous = OFF')
        self.cursor.execute('PRAGMA journal_mode = MEMORY')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, lat REAL, lon REAL, tags TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ways (id INTEGER PRIMARY KEY, nodes TEXT, tags TEXT)''')
        self.conn.commit()
        
        self.node_count = 0
        self.way_count = 0
        self.total_nodes = total_nodes
        self.total_ways = total_ways
        self.total_elements = total_nodes + total_ways
        self.last_update = time.time()
        self.batch_size = 10000

    def node(self, n):
        self.cursor.execute('''INSERT INTO nodes (id, lat, lon, tags) VALUES (?, ?, ?, ?)''', 
                            (n.id, n.location.lat, n.location.lon, str(dict(n.tags))))
        self.node_count += 1
        self._check_commit()

    def way(self, w):
        self.cursor.execute('''INSERT INTO ways (id, nodes, tags) VALUES (?, ?, ?)''', 
                            (w.id, ' '.join(map(str, w.nodes)), str(dict(w.tags))))
        self.way_count += 1
        self._check_commit()

    def _check_commit(self):
        if (self.node_count + self.way_count) % self.batch_size == 0:
            self.conn.commit()
            self._update_progress()

    def _update_progress(self):
        current_time = time.time()
        if current_time - self.last_update >= 20:
            total_processed = self.node_count + self.way_count
            progress_percentage = (total_processed / self.total_elements) * 100
            print(f"Processed {self.node_count} nodes and {self.way_count} ways ({progress_percentage:.2f}%)")
            self.last_update = current_time

def get_total_elements(filename):
    result = subprocess.run(['osmium', 'fileinfo', '-e', filename], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    nodes = 0
    ways = 0
    for line in lines:
        if 'Number of nodes:' in line:
            nodes = int(line.split(':')[1].strip())
        elif 'Number of ways:' in line:
            ways = int(line.split(':')[1].strip())
    if nodes == 0 or ways == 0:
        raise ValueError(f"Could not parse node and way counts from osmium output: {result.stdout}")
    return nodes, ways

# Get total number of nodes and ways
print("Analyzing file...")
total_nodes, total_ways = get_total_elements('norway-latest.osm.pbf')
print(f"File contains {total_nodes} nodes and {total_ways} ways")

# Load the OpenStreetMap file in pbf format
handler = OsmHandler(total_nodes, total_ways)
print("Starting conversion...")
handler.apply_file('norway-latest.osm.pbf')

# Save final changes to the database
handler.conn.commit()
handler.conn.close()
print(f"Conversion complete. Processed {handler.node_count} nodes and {handler.way_count} ways")
