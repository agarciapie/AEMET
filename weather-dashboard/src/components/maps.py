import plotly.express as px
import streamlit as st
import pandas as pd
import logging
import tracemalloc

# Enable tracemalloc
tracemalloc.start()

# Configure logging
logger = logging.getLogger(__name__)

def validate_map_data(df):
    """Validate dataframe for map creation"""
    required_cols = ['latitud', 'longitud', 'nombre', 'provincia', 'altitud']
    if not all(col in df.columns for col in required_cols):
        logger.error(f"Missing required columns. Found: {df.columns.tolist()}")
        return False
    return True

@st.cache_data(ttl=3600)
def create_stations_map(df, selected_station=None):
    """Create interactive map with station selection"""
    try:
        if df.empty or not validate_map_data(df):
            st.error("Invalid data format for map")
            return None
            
        # Convert coordinates to numeric
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        
        # Highlight selected station if any
        df['selected'] = df['nombre'] == selected_station
        
        # Create map
        fig = px.scatter_mapbox(
            df.dropna(subset=['latitud', 'longitud']),
            lat='latitud',
            lon='longitud',
            hover_name='nombre',
            hover_data={
                'provincia': True,
                'altitud': ':.0f',
                'latitud': ':.4f',
                'longitud': ':.4f'
            },
            color='selected',  # Highlight selected station
            color_discrete_map={True: 'red', False: 'blue'},
            zoom=5,
            center={"lat": 40.4168, "lon": -3.7038},
            height=600,
            title="Estaciones Meteorológicas"
        )
        
        # Configure layout
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":30,"l":0,"b":0},
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating map: {str(e)}")
        st.error("Error creating map visualization")
        return None

def station_selector(df):
    """Create station selection widget"""
    provinces = ['Todas'] + sorted(df['provincia'].unique().tolist())
    
    # Province filter
    province = st.sidebar.selectbox("Provincia:", provinces)
    
    # Filter stations by province
    filtered_df = df if province == 'Todas' else df[df['provincia'] == province]
    
    # Station selector
    station = st.sidebar.selectbox(
        "Estación:",
        sorted(filtered_df['nombre'].unique().tolist())
    )
    
    return station, filtered_df

def display_station_data(df, station_name):
    """Display selected station data"""
    if station_name:
        station = df[df['nombre'] == station_name].iloc[0]
        
        # Create three columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Altitud", f"{station['altitud']:.0f}m")
        with col2:
            st.metric("Latitud", f"{station['latitud']:.4f}°")
        with col3:
            st.metric("Longitud", f"{station['longitud']:.4f}°")
            
        # Additional station info
        st.subheader("Información de la Estación")
        st.write(f"**Provincia:** {station['provincia']}")
        st.write(f"**Nombre:** {station['nombre']}")

def display_map(df):
    """Display map in Streamlit"""
    station, filtered_df = station_selector(df)
    fig = create_stations_map(filtered_df, selected_station=station)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        display_station_data(df, station)
    else:
        st.warning("No map data available")