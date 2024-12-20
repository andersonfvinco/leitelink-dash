import pandas as pd
import pyarrow.parquet as pq
import geopandas as gpd
import boto3
from dotenv import load_dotenv
import os
import io

load_dotenv()

# Configuração das credenciais AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = "us-east-2"  # Ajuste conforme necessário


def carrega_mapa():
    
    #uploaded_file = 'data//110m_cultural.zip'
    #gdf = gpd.read_file(f"zip://{uploaded_file}", layer="ne_110m_admin_0_countries") #ne_110m_populated_places, ne_110m_admin_0_countries

    # Caminho absoluto baseado na localização do script
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "data", "110m_cultural.zip")
    gdf = gpd.read_file(f"zip://{file_path}", layer="ne_110m_admin_0_countries") #ne_110m_populated_places, ne_110m_admin_0_countries

    # Reprojetar para um CRS projetado (por exemplo, Mercator)
    gdf_projected = gdf.to_crs(epsg=3857)
    
    # Calcular os centroides no sistema projetado
    gdf_projected["centroid"] = gdf_projected.geometry.centroid
    
    # Reprojetar os centroides de volta para WGS84
    gdf["lon"] = gdf_projected["centroid"].to_crs(epsg=4326).x
    gdf["lat"] = gdf_projected["centroid"].to_crs(epsg=4326).y

    gdf = gdf.drop(columns=["geometry"], errors="ignore")

    return gdf


def read_txt_file_from_s3(bucket_name, file_name):
    """Lê um arquivo .txt do S3 e retorna seu conteúdo como string."""
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )
    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    data = response["Body"].read()
    return data.decode("utf-8")  # Decodifica o conteúdo como texto


def write_txt_to_s3(bucket_name, file_name, content):
    """
    Escreve conteúdo em um arquivo .txt no S3.

    Args:
        bucket_name (str): Nome do bucket S3.
        file_name (str): Caminho do arquivo no bucket.
        content (str): Conteúdo a ser escrito no arquivo.

    Returns:
        str: URL público do arquivo se o upload for bem-sucedido.
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )

    # Converte o conteúdo para bytes
    content_bytes = content.encode("utf-8")

    # Faz o upload do conteúdo como arquivo
    s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=content_bytes)


def read_parquet_from_s3(bucket_name, file_name):
    """Lê um arquivo Parquet do S3 e retorna um DataFrame."""
    # Configura o cliente S3
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )
    
    # Baixa o arquivo do S3 para um objeto BytesIO
    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    parquet_data = response["Body"].read()  # Lê o corpo da resposta como bytes
    
    # Lê o Parquet com pandas
    df = pd.read_parquet(io.BytesIO(parquet_data), engine="pyarrow")
    return df