# climatechic_mvp_poc.py
# Fixed for Windows compatibility

import geopandas as gpd
import pandas as pd
import folium
from folium import plugins
from shapely.geometry import Polygon, shape
import json
import random
import os
from datetime import datetime

print("🚀 Starting ClimateChic MVP Simulation (Local Machine)")

# ==============================================
# 1. SIMULATE DATA STORAGE
# ==============================================
FLORA_DATABASE = {
    "Tropical_Rainforest": [
        {"name": "Leucaena leucocephala", "type": "Tree", "chicken_benefit": "High-protein forage, shade"},
        {"name": "Moringa oleifera", "type": "Tree", "chicken_benefit": "Vitamins, minerals, forage"},
        {"name": "Paspalum notatum", "type": "Grass", "chicken_benefit": "Ground cover, forage"},
    ],
    "Tropical_Savanna": [
        {"name": "Acacia tortilis", "type": "Tree", "chicken_benefit": "Shade, pods for forage"},
        {"name": "Cenchrus ciliaris", "type": "Grass", "chicken_benefit": "Drought-resistant forage"},
    ]
}

# Create biogeographic regions
dummy_regions_data = {
    'name': ['Tropical_Rainforest_Region', 'Tropical_Savanna_Region'],
    'geometry': [
        Polygon([(33.5, -1.5), (35.5, -1.5), (35.5, 1.5), (33.5, 1.5), (33.5, -1.5)]),
        Polygon([(36.0, -2.0), (38.0, -2.0), (38.0, 0.5), (36.0, 0.5), (36.0, -2.0)])
    ]
}
BIOGEO_REGIONS_GDF = gpd.GeoDataFrame(dummy_regions_data, crs="EPSG:4326")

# ==============================================
# 2. CORE GEOAI FUNCTIONS (REUSABLE)
# ==============================================

def analyze_land(boundary_gdf):
    """Analyze land and generate restoration plan."""
    plan = {}
    # FIXED: Use union_all() instead of deprecated unary_union
    boundary_geom = boundary_gdf.geometry.union_all()
    
    # Region analysis
    intersected_region = None
    max_overlap = 0
    for idx, region in BIOGEO_REGIONS_GDF.iterrows():
        if boundary_geom.intersects(region.geometry):
            overlap_area = boundary_geom.intersection(region.geometry).area
            overlap_percentage = (overlap_area / boundary_geom.area) * 100
            if overlap_percentage > max_overlap:
                max_overlap = overlap_percentage
                intersected_region = region['name']
    
    region_key = intersected_region.split('_Region')[0] if intersected_region else "Tropical_Savanna"
    plan['biogeographic_region'] = region_key
    plan['recommended_flora'] = FLORA_DATABASE.get(region_key, [])
    
    # Simulation
    area_hectares = boundary_geom.area * 10000
    plan['simulation'] = {
        'land_area_hectares': round(area_hectares, 2),
        'estimated_trees_year_5': int(area_hectares * 100),
        'estimated_chickens_year_2': int(area_hectares * 50),
        'black_soldier_fly_production_kg_week': int(area_hectares * 2),
        'region_overlap_percentage': round(max_overlap, 1)
    }
    
    return plan

def generate_plan_report(plan):
    """Generate restoration plan report."""
    # FIXED: Remove emojis for Windows compatibility
    report = f"""CLIMATECHIC RESTORATION PLAN
==================================================
Region: {plan['biogeographic_region']}
Area: {plan['simulation']['land_area_hectares']} hectares
Region Overlap: {plan['simulation']['region_overlap_percentage']}%

RECOMMENDED FLORA:
"""
    for flora in plan['recommended_flora']:
        report += f"* {flora['name']} ({flora['type']}) - {flora['chicken_benefit']}\n"
    
    report += f"""
PROJECTIONS:
* Trees (Year 5): {plan['simulation']['estimated_trees_year_5']}
* Chickens (Year 2): {plan['simulation']['estimated_chickens_year_2']}
* BSF Production: {plan['simulation']['black_soldier_fly_production_kg_week']} kg/week

OPERATIONAL GUIDELINES:
* Months 1-3: Soil preparation and pioneer species planting
* Months 4-6: Introduce nitrogen-fixing plants and cover crops
* Months 7-12: Establish poultry infrastructure and initial flock
* Year 2: Scale integrated systems and value-added production
"""
    return report

# ==============================================
# 3. BOUNDARY PROCESSING FUNCTIONS
# ==============================================

def process_geojson_file(geojson_path):
    """Process a GeoJSON file and generate analysis."""
    try:
        print(f"Processing: {geojson_path}")
        boundary_gdf = gpd.read_file(geojson_path)
        restoration_plan = analyze_land(boundary_gdf)
        report = generate_plan_report(restoration_plan)
        
        # Save report to text file with UTF-8 encoding for Windows
        report_filename = geojson_path.replace('.geojson', '_report.txt')
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Analysis complete! Report saved: {report_filename}")
        print("\n" + "="*50)
        print(report)
        print("="*50)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()

def create_interactive_map():
    """Create map with drawing tools."""
    m = folium.Map(location=[-1.225, 36.775], zoom_start=12)
    
    # Add basemaps
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite'
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Terrain'
    ).add_to(m)
    
    folium.TileLayer('CartoDB dark_matter', name='Dark Mode').add_to(m)
    folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
    
    # Add drawing tools
    draw_options = {
        'polyline': False,
        'rectangle': True,
        'circle': False,
        'marker': False,
        'circlemarker': False,
        'polygon': True,
    }
    
    # Custom HTML for download button
    download_html = '''
    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.2);">
        <h4>ClimateChic Tools</h4>
        <p>1. Draw your boundary</p>
        <p>2. Click download button to save GeoJSON</p>
        <p>3. Run: python climatechic_mvp_poc.py YOUR_FILE.geojson</p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(download_html))
    
    draw_control = plugins.Draw(
        export=True,
        draw_options=draw_options,
        edit_options={'edit': True}
    )
    draw_control.add_to(m)
    
    plugins.MeasureControl().add_to(m)
    folium.LayerControl().add_to(m)
    
    # Add instructions popup
    instructions = '''
    <h3>ClimateChic Instructions</h3>
    <ol>
    <li>Use drawing tools to create your farm boundary</li>
    <li>Click the download button to save as GeoJSON</li>
    <li>Run the analysis script on the downloaded file</li>
    </ol>
    '''
    
    folium.Marker(
        [-1.225, 36.775],
        icon=folium.DivIcon(html='<div style="font-size: 24px; color: green;">!</div>'),
        popup=folium.Popup(instructions, max_width=300)
    ).add_to(m)
    
    m.save('climatechic_drawing_tool.html')
    print("Drawing tool created: climatechic_drawing_tool.html")
    return m

# ==============================================
# 4. MAIN EXECUTION
# ==============================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # If a file is provided as argument, process it
        process_geojson_file(sys.argv[1])
    else:
        # Otherwise, create the drawing tool
        print("Creating ClimateChic Drawing Tool...")
        print("Default location: Nairobi, Kenya")
        create_interactive_map()
        print("\nINSTRUCTIONS:")
        print("1. Open 'climatechic_drawing_tool.html' in your browser")
        print("2. Draw your farm boundary using the drawing tools")
        print("3. Click the download button to save as GeoJSON")
        print("4. Run: python climatechic_mvp_poc.py YOUR_FILE.geojson")