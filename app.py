import streamlit as st
import pandas as pd
import folium
from folium.plugins import PolyLineTextPath
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Wczytaj istniejące trasy z pliku CSV
@st.cache_data
def load_trasy():
    df = pd.read_csv("trasy.csv")
    return df

trasy_df = load_trasy()

# Funkcja pomocnicza do geokodowania nazw miejscowości
@st.cache_data
def geocode_city(city_name):
    geolocator = Nominatim(user_agent="streamlit_app")
    location = geolocator.geocode(city_name + ", Poland")
    if location:
        return location.latitude, location.longitude
    return None, None

st.set_page_config(page_title="Mapa Tras w Polsce", layout="wide")
st.title("🚚 Interaktywna mapa tras transportowych w Polsce")

# Wprowadź miejscowości
col1, col2 = st.columns(2)
with col1:
    miejsce_z = st.text_input("Z (miejsce startowe)")
with col2:
    miejsce_do = st.text_input("Do (miejsce docelowe)")

# Inicjalna mapa (pusta)
mapa = folium.Map(location=[52.0, 19.0], zoom_start=6)

# Rysuj istniejące trasy jeśli wpisano Z i Do
if miejsce_z and miejsce_do:
    lat_z, lon_z = geocode_city(miejsce_z)
    lat_do, lon_do = geocode_city(miejsce_do)

    if None in (lat_z, lon_z, lat_do, lon_do):
        st.error("Nie można znaleźć jednej z lokalizacji. Upewnij się, że poprawnie wpisałeś miejscowości.")
    else:
        # Dodaj marker dla Z i Do
        folium.Marker([lat_z, lon_z], tooltip=f"Start: {miejsce_z}", icon=folium.Icon(color='green')).add_to(mapa)
        folium.Marker([lat_do, lon_do], tooltip=f"Cel: {miejsce_do}", icon=folium.Icon(color='red')).add_to(mapa)

        # Dodaj trasę główną
        linia = folium.PolyLine(locations=[[lat_z, lon_z], [lat_do, lon_do]], color="blue", weight=5).add_to(mapa)
        PolyLineTextPath(linia, "➡", repeat=True, offset=7, attributes={"fill": "blue", "font-weight": "bold", "font-size": "16"}).add_to(mapa)

        # Szukaj najbliższych istniejących tras
        nowa_start = (lat_z, lon_z)
        nowa_end = (lat_do, lon_do)

        for _, row in trasy_df.iterrows():
            punkt_a = (row['lat_z'], row['lon_z'])
            punkt_b = (row['lat_do'], row['lon_do'])

            dist_a = geodesic(nowa_start, punkt_a).km
            dist_b = geodesic(nowa_end, punkt_b).km

            if dist_a < 50 or dist_b < 50:
                folium.PolyLine(locations=[punkt_a, punkt_b], color="gray", weight=2, opacity=0.6).add_to(mapa)

# Wyświetl mapę
st_folium(mapa, width=1000, height=600)

