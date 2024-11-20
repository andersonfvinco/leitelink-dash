import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import json

# Configurações do Streamlit
st.set_page_config(page_title="Dashboard Georreferenciado", layout="wide")

# Título do dashboard
st.title("Dashboard Georreferenciado")

# Carregar dados geográficos (GeoJSON ou shapefile)
uploaded_file = '110m_cultural.zip'

if uploaded_file:
    try:
        gdf = gpd.read_file(f"zip://{uploaded_file}", layer="ne_110m_admin_0_countries") #ne_110m_populated_places, ne_110m_admin_0_countries
        
        # Reprojetar para um CRS projetado (por exemplo, Mercator)
        gdf_projected = gdf.to_crs(epsg=3857)
        
        # Calcular os centroides no sistema projetado
        gdf_projected["centroid"] = gdf_projected.geometry.centroid
        
        # Reprojetar os centroides de volta para WGS84
        gdf["lon"] = gdf_projected["centroid"].to_crs(epsg=4326).x
        gdf["lat"] = gdf_projected["centroid"].to_crs(epsg=4326).y

        gdf = gdf.drop(columns=["geometry"], errors="ignore")
        
        # Seleção de colunas para exibição
        st.sidebar.header("Opções de visualização")
        column_to_display = st.sidebar.selectbox("Escolha uma coluna para colorir o mapa:", gdf.columns)

        # # Criação do mapa com Plotly
        # fig = px.scatter_mapbox(
        #     gdf,
        #     lat="lat",
        #     lon="lon",
        #     color=column_to_display,
        #     hover_name=gdf.index,
        #     hover_data=gdf.columns,
        #     mapbox_style="carto-positron",
        #     zoom=3,
        #     height=600,
        #     title="Mapa Georreferenciado"
        # )

        geojson = json.loads(gdf.to_json())
        fig = px.choropleth_mapbox(
            gdf,
            geojson=geojson,
            locations=gdf.index,
            #color=column_to_display,
            mapbox_style="carto-positron",
            title="Mapa Georreferenciado",
            height=600,
            zoom=1
        )

        # Criar DataFrame com o ponto personalizado
        point_df = pd.DataFrame({
            "lat": [-20.377197],
            "lon": [-40.361822],
            "label": ["Ponto Personalizado"]
        })

        # Adicionar o ponto ao mapa
        fig.add_scattermapbox(
            lat=point_df["lat"],
            lon=point_df["lon"],
            mode="markers",
            marker=dict(size=10, color="blue"),
            text=point_df["label"],
            name="Ponto Personalizado"
        )

        # Renderizar o mapa no Streamlit
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, faça o upload de um arquivo GeoJSON ou shapefile (em .zip).")
