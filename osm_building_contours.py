import osmnx as ox
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import st_folium
import tempfile
import zipfile
import os

def fetch_building_contours(lat, lon, distance=800):
    # Fetch buildings data from OSM
    point = (lat, lon)
    gdf = ox.geometries_from_point(point, tags={'building': True}, dist=distance)
    gdf = gdf[gdf.geometry.type == 'Polygon']  # Filter only Polygon geometries
    return gdf

def visualize_buildings_on_map(gdf, lat, lon):
    # Create a folium map centered around the buildings
    m = folium.Map(location=[lat, lon], zoom_start=16)
    
    # Add building contours to the map
    folium.GeoJson(gdf).add_to(m)
    
    return m

def main():
    st.title("Building Contours Viewer from OSM")

    # Input for placemark (latitude and longitude)
    lat = st.number_input("Enter latitude", value=32.0853, step=0.0001, format="%.4f")
    lon = st.number_input("Enter longitude", value=34.7818, step=0.0001, format="%.4f")

    if st.button("Fetch and Display Building Contours"):
        try:
            gdf = fetch_building_contours(lat, lon)
            if gdf.empty:
                st.warning("No building contours found for the specified location.")
            else:
                st.success(f"Found {len(gdf)} building contours.")
                
                # Display map
                contour_map = visualize_buildings_on_map(gdf, lat, lon)
                st_data = st_folium(contour_map, width=700, height=500)
                
                # Create temporary files for KML and SHP
                with tempfile.TemporaryDirectory() as tmpdirname:
                    kml_path = os.path.join(tmpdirname, "building_contours.kml")
                    shp_path = os.path.join(tmpdirname, "building_contours.shp")
                    gdf.to_file(kml_path, driver='KML')
                    gdf.to_file(shp_path)

                    # Create ZIP file for SHP
                    zip_path = os.path.join(tmpdirname, "building_contours_shp.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for shp_file in os.listdir(tmpdirname):
                            if shp_file.startswith("building_contours"):
                                zipf.write(os.path.join(tmpdirname, shp_file), shp_file)

                    # Provide download links
                    with open(kml_path, "rb") as kml_file:
                        st.download_button(label="Download KML", data=kml_file, file_name="building_contours.kml")
                    
                    with open(zip_path, "rb") as zip_file:
                        st.download_button(label="Download SHP (ZIP)", data=zip_file, file_name="building_contours_shp.zip")
                
        except Exception as e:
            st.error(f"An error occurred while fetching building contours: {e}")

if __name__ == "__main__":
    main()
