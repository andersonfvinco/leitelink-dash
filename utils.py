import geopandas as gpd

def carrega_mapa():
    
    uploaded_file = '110m_cultural.zip'
    gdf = gpd.read_file(f"zip://{uploaded_file}", layer="ne_110m_admin_0_countries") #ne_110m_populated_places, ne_110m_admin_0_countries
    
    # Reprojetar para um CRS projetado (por exemplo, Mercator)
    gdf_projected = gdf.to_crs(epsg=3857)
    
    # Calcular os centroides no sistema projetado
    gdf_projected["centroid"] = gdf_projected.geometry.centroid
    
    # Reprojetar os centroides de volta para WGS84
    gdf["lon"] = gdf_projected["centroid"].to_crs(epsg=4326).x
    gdf["lat"] = gdf_projected["centroid"].to_crs(epsg=4326).y

    gdf = gdf.drop(columns=["geometry"], errors="ignore")

    return gdf