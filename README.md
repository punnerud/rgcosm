# RGCosm - Reverse Geocode for OpenStreetmap

Locally hosted OpenStreetmap using sqlite3 for reverse geocode.
So you easily can find adresses based on coordinates.

Download the pbf file from:
https://download.geofabrik.de/

Then use convert.py to create the database:
```
python3 convert.py
```

You have to change "norway-latest.osm.pbf" in convert.py into your filename.
The "norway-latest.osm.pbf" is about 1GB and the sqlite3 end up 10GB. With indexes 16GB. So don't try with the biggest areas for starting. Takes about 15minutes for the norway file.

To speed up your queries it is highly recommended to add indexes. This increase the size around 50% and takes a couple of minutes to create:
```
CREATE INDEX "nodes index lat" ON "nodes" ( "lat" );
CREATE INDEX "nodes index lon" ON "nodes" ( "lon" );
```

Adding indexes change the search time for my Norway file from 10 to 0.15 seconds. Changing the lookaround query can also reduce the search time, at the risk that you miss an adress if the closest adress is more far away.


Mac users, I found this to work for installation of osmium for Python:
```
brew install cmake
brew install wheel
brew install osmium-tool
python3 -m pip install osmium
```
