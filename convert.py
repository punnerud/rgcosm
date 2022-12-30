import os
import osmium
import sqlite3

class OsmHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.conn = sqlite3.connect('osm.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, lat REAL, lon REAL, tags TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ways (id INTEGER PRIMARY KEY, nodes INTEGER, tags TEXT)''')
        self.conn.commit()

    def node(self, n):
        self.cursor.execute('''INSERT INTO nodes (id, lat, lon, tags) VALUES (?, ?, ?, ?)''', (n.id, n.location.lat, n.location.lon, str(dict(n.tags))))
        self.conn.commit()

    def way(self, w):
        self.cursor.execute('''INSERT INTO ways (id, nodes, tags) VALUES (?, ?, ?)''', (w.id, ' '.join(map(str, w.nodes)), str(dict(w.tags))))
        self.conn.commit()

# Last opp OpenStreetMap-filen i pbf-format
handler = OsmHandler()
handler.apply_file('norway-latest.osm.pbf')

# Lagre endringer i databasen
handler.conn.commit()
handler.conn.close()
