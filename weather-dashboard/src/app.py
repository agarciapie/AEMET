"""
Weather Dashboard main application
Features:
- Interactive map of weather stations
- Province-based filtering
- Station selection and details
- Current weather data display
- Data export functionality
"""

import streamlit as st
import plotly.express as px
from api.weather_data import WeatherData
import pandas as pd
from utils.helpers import format_dataframe
from utils.helpers import display_station_weather, get_station_weather

# Page config
st.set_page_config(page_title="Weather Stations", layout="wide")

# Constants
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZ2FyY2lhcGllQGdtYWlsLmNvbSIsImp0aSI6ImVjNDdjM2U4LTA5YzctNDdmNS1hNTUzLTBkMTc5MzU5MWE5ZCIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzM4NzA2NDIyLCJ1c2VySWQiOiJlYzQ3YzNlOC0wOWM3LTQ3ZjUtYTU1My0wZDE3OTM1OTFhOWQiLCJyb2xlIjoiIn0.aKNG9qapyR_2Bk8maBPZO5NMUJ-6PckD430I-0Z2jKQ"

@st.cache_resource
def get_weather_api():
    return WeatherData(API_KEY)

@st.cache_data(ttl=3600)
def load_stations():
    weather = get_weather_api()
    return weather.get_stations()

# Main app
st.title("🌤️ Estaciones metereológicas en España")

try:
    # Load and format data
    df = load_stations()
    df = format_dataframe(df)

    if not df.empty:
        # Add province filter in sidebar
        st.sidebar.subheader("Filtros")
        provinces = ['Todas'] + sorted(df['provincia'].unique().tolist())
        selected_province = st.sidebar.selectbox("Provincia:", provinces)

        # Filter data by province
        if selected_province != 'Todas':
            filtered_df = df[df['provincia'] == selected_province]
        else:
            filtered_df = df

        # Update map with filtered data
        fig = px.scatter_map(
            filtered_df,
            lat='latitud',
            lon='longitud',
            hover_name='nombre',
            hover_data={
                'provincia': True,
                'altitud': ':.0f',
                'latitud': ':.4f',
                'longitud': ':.4f'
            },
            zoom=5,
            center={"lat": 40.4168, "lon": -3.7038}
        )

        fig.update_layout(
            margin={"r":0,"t":30,"l":0,"b":0},
            height=600,
            showlegend=False,
            mapbox=dict(
                style="open-street-map",
                zoom=5,
                center=dict(lat=40.4168, lon=-3.7038)
            )
        )
        
        # Display map
        st.plotly_chart(fig, use_container_width=True)
        
        # Add metrics above the map
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Estaciones", len(filtered_df))
        with col2:
            st.metric("Provincias", len(filtered_df['provincia'].unique()))
        with col3:
            st.metric("Altitud Media", f"{filtered_df['altitud'].mean():.0f}m")
        
        # Add station selector
        st.sidebar.subheader("Seleccionar Estación")
        selected_station = st.sidebar.selectbox(
            "Estación Meteorológica",
            options=filtered_df['nombre'].unique(),
            format_func=lambda x: f"{x} ({filtered_df[filtered_df['nombre']==x]['provincia'].iloc[0]})"
        )
        
        # Show station weather data
        if selected_station:
            st.subheader(f"Datos Meteorológicos - {selected_station}")
            station_id = df[df['nombre'] == selected_station]['indicativo'].iloc[0]
            weather_data = get_station_weather(API_KEY, station_id)
            display_station_weather(df[df['nombre'] == selected_station].iloc[0], weather_data)
        
        # Show data table
        st.subheader("Informacion Estaciones metereológicas")
        st.dataframe(df)
        
        # Add download button for data
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            "Descargar Datos (CSV)",
            csv,
            "estaciones_meteorologicas.csv",
            "text/csv",
            key='download-csv'
        )
        
    else:
        st.error("No data available")
        
except Exception as e:
    st.error(f"Error: {str(e)}")