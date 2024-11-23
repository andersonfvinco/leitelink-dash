import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
from utils import *
import json


st.set_page_config(
    page_title='LeiteLink',
    layout='wide'
)

# Adicionando CSS personalizado para ajustar o container à largura máxima
st.markdown("""
    <style>
        .main .block-container {
            width: 96% !important;
            max-width: 96% !important;
            padding-left: 2 !important;
            padding-right: 2 !important;
        }
        .stApp {
            width: 100% !important;
        }
        
        @media (max-width: 800px) {
            /* Quando a largura da tela for menor que 800px, as colunas ficam empilhadas */
            .stColumn {
                width: 100% !important;
                padding: 0 !important;
            }
        }
        @media (min-width: 801px) {
            /* Quando a largura da tela for maior que 800px, as colunas ficam lado a lado */
            .stColumn {
                width: 48% !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

gdf = carrega_mapa()

st.title("LeiteLink - Monitoramento e Controle de Tanques de Resfriamento")

col1, col2 = st.columns(2)


with col1:
    
    #st.header("Col1")

    geojson = json.loads(gdf.to_json())
    fig = px.choropleth_mapbox(
        gdf,
        geojson=geojson,
        locations=gdf.index,
        mapbox_style="carto-positron",
        height=600,
        zoom=5,
        center={"lat":-19.902460, "lon":-43.958864} #Estamos considerando a cidade de BH como centro
    )

    # Criar DataFrame com o ponto personalizado
    point_df = pd.DataFrame({
        "lat": [-20.377197],
        "lon": [-40.361822],
        "label": ["Fazenda X"]
    })

    # Adicionar o ponto ao mapa
    fig.add_scattermapbox(
        lat=point_df["lat"],
        lon=point_df["lon"],
        mode="markers",
        marker=dict(size=10, color="blue"),
        text=point_df["label"],
        name=""
    )
    fig.update_layout(autosize=True,
                      margin={"r":0,"t":0,"l":0,"b":0},
                      showlegend=False
                  )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    
    #st.header("Col2")
    equipamento = st.selectbox(
        "Selecione o tanque:", ['equip1', 'equip2', 'equip3'], index=0
    )
    ligar_tanque = st.checkbox(
        "Ligar tanque"
    )
    if ligar_tanque:
        write_txt_to_s3(bucket_name='poc-leitelink', file_name='prototipo1/comando.txt', content='Ligar')
    else:
        write_txt_to_s3(bucket_name='poc-leitelink', file_name='prototipo1/comando.txt', content='Desligar')
    
    df = pd.read_parquet('sample_data.parquet')
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.075)

    fig.add_trace(go.Scatter(
        x=df['time'], y=df['raw_int'], name='AD', mode='lines+markers'), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['time'], y=df['Pressure_mV'], name='mV', mode='lines+markers'), row=2, col=1)
    
    fig.update_layout(autosize=True,
                    margin={"r":0,"t":0,"l":0,"b":0},
                    showlegend=False
                )

    st.plotly_chart(fig, use_container_width=True)

