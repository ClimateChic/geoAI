# climatechic_simple.py
import geopandas as gpd
from shapely.geometry import Polygon
import webbrowser
import os

def create_simple_map():
    """Create a simple HTML map with drawing tools"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>ClimateChic Simple</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        #map { height: 100vh; width: 100%; }
        .info { position: absolute; top: 10px; right: 10px; background: white; padding: 10px; z-index: 1000; }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info">
        <h3>Draw your farm boundary</h3>
        <p>Right-click → Save as GeoJSON</p>
        <p>Then run: python analyze.py your_file.geojson</p>
    </div>
    
    <script>
        const map = L.map('map').setView([-1.286, 36.817], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        
        let drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);
        
        // Enable drawing
        map.on('click', function(e) {
            if (!window.polygon) {
                window.polygon = L.polygon([e.latlng]);
                drawnItems.addLayer(window.polygon);
            } else {
                window.polygon.addLatLng(e.latlng);
            }
        });
        
        // Right-click to finish
        map.on('contextmenu', function(e) {
            if (window.polygon) {
                const geoJSON = window.polygon.toGeoJSON();
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(geoJSON));
                const downloadAnchorNode = document.createElement('a');
                downloadAnchorNode.setAttribute("href", dataStr);
                downloadAnchorNode.setAttribute("download", "farm_boundary.geojson");
                document.body.appendChild(downloadAnchorNode);
                downloadAnchorNode.click();
                downloadAnchorNode.remove();
                window.polygon = null;
            }
        });
    </script>
</body>
</html>
    """
    
    with open('simple_map.html', 'w') as f:
        f.write(html_content)
    
    webbrowser.open('simple_map.html')

if __name__ == "__main__":
    create_simple_map()