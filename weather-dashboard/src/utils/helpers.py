import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def convert_coordinate(coord_str):
    """
    Converts AEMET coordinate format to decimal degrees
    
    Args:
        coord_str (str): Coordinate string (e.g., '394924N' for 39°49'24"N)
    
    Returns:
        float: Decimal degrees
    """
    try:
        if isinstance(coord_str, (int, float)):
            return float(coord_str)
            
        coord_str = str(coord_str).strip()
        if not coord_str:
            return None
            
        direction = coord_str[-1].upper()
        numeric_part = coord_str[:-1]
        
        if len(numeric_part) == 6:  # Format DDMMSS
            degrees = float(numeric_part[:2])
            minutes = float(numeric_part[2:4])
            seconds = float(numeric_part[4:])
            
            # Validate ranges
            if not (0 <= degrees <= 90 and 0 <= minutes < 60 and 0 <= seconds < 60):
                logger.error(f"Invalid coordinate values: {degrees}° {minutes}' {seconds}\"")
                return None
                
            # Convert to decimal degrees
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Adjust for hemisphere
            if direction in ['S', 'W']:
                decimal = -decimal
                
            # Log conversion for verification
            logger.debug(f"Converted {coord_str} to {decimal:.6f}° ({degrees}° {minutes}' {seconds}\" {direction})")
            
            return decimal
        else:
            logger.error(f"Invalid coordinate format: {coord_str}")
            return None
            
    except Exception as e:
        logger.error(f"Error converting coordinate {coord_str}: {str(e)}")
        return None

def format_dataframe(df):
    """
    Formats weather station dataframe
    
    Args:
        df (pd.DataFrame): Raw station data
    
    Returns:
        pd.DataFrame: Processed data with converted coordinates
    """
    if df.empty:
        return df
        
    df = df.copy()
    
    try:
        # Convert coordinates
        df['latitud'] = df['latitud'].apply(convert_coordinate)
        df['longitud'] = df['longitud'].apply(convert_coordinate)
        
        # Round values
        df['latitud'] = df['latitud'].round(6)
        df['longitud'] = df['longitud'].round(6)
        df['altitud'] = pd.to_numeric(df['altitud'], errors='coerce').round(0)
        
        # Drop invalid coordinates
        df = df.dropna(subset=['latitud', 'longitud'])
        
        # Log some coordinates for verification
        print("Sample coordinates after conversion:")
        print(df[['nombre', 'latitud', 'longitud']].head())
        
        return df
        
    except Exception as e:
        st.error(f"Error formatting data: {str(e)}")
        return df

def format_data(df):
    """Format dataframe columns for display"""
    if df.empty:
        return df
        
    formatted_df = df.copy()
    
    # Convert and round numeric columns
    numeric_cols = {
        'altitud': 2,
        'latitud': 4,
        'longitud': 4
    }
    
    for col, decimals in numeric_cols.items():
        if col in formatted_df.columns:
            formatted_df[col] = pd.to_numeric(formatted_df[col], errors='coerce')
            formatted_df[col] = formatted_df[col].round(decimals)
    
    # Clean text columns
    text_columns = ['nombre', 'provincia']
    for col in text_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].str.strip().str.title()
    
    return formatted_df

def get_unique_provinces(df):
    """Get sorted list of unique provinces"""
    if 'provincia' in df.columns:
        return sorted(df['provincia'].unique().tolist())
    return []

def calculate_metrics(df):
    """Calculate dashboard metrics"""
    metrics = {
        'total_stations': len(df),
        'avg_altitude': df['altitud'].mean() if 'altitud' in df.columns else 0,
        'total_provinces': len(df['provincia'].unique()) if 'provincia' in df.columns else 0
    }
    return metrics

def process_coordinates(df):
    """Process and validate coordinates"""
    try:
        logger.debug(f"Input DataFrame columns: {df.columns.tolist()}")
        logger.debug(f"Sample data:\n{df.head()}")
        
        required_cols = ['latitud', 'longitud', 'nombre', 'provincia', 'altitud']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Missing columns. Available: {df.columns.tolist()}")
            return None
            
        # Clean and convert coordinates
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        
        # Remove invalid coordinates
        df = df.dropna(subset=['latitud', 'longitud'])
        
        # Log coordinate ranges
        logger.debug(f"Latitude range: {df['latitud'].min()} to {df['latitud'].max()}")
        logger.debug(f"Longitude range: {df['longitud'].min()} to {df['longitud'].max()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing coordinates: {str(e)}")
        st.error(f"Data processing error: {str(e)}")
        return None

def create_weather_map(df):
    """Create interactive weather stations map"""
    try:
        df = process_coordinates(df)
        if df is None or df.empty:
            return None
            
        # Create map with explicit configuration
        fig = px.scatter_mapbox(
            df,
            lat='latitud',
            lon='longitud',
            hover_name='nombre',
            hover_data=['provincia', 'altitud'],
            zoom=5,
            center={"lat": 40.4168, "lon": -3.7038},
            title="Estaciones Meteorológicas",
            height=700,
            width=1000
        )
        
        # Configure layout
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                zoom=5,
                center=dict(lat=40.4168, lon=-3.7038)
            ),
            showlegend=False,
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        
        # Render in Streamlit with specific settings
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        return fig
        
    except Exception as e:
        logger.error(f"Error creating map: {str(e)}")
        st.error(f"Map creation error: {str(e)}")
        return None

def display_map(df):
    """Display map with loading state"""
    with st.spinner('Loading map...'):
        fig = create_weather_map(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Could not display map - please check data format")

def get_station_weather(api_key, station_id):
    """Fetch current weather data for a specific station"""
    try:
        base_url = "https://opendata.aemet.es/opendata/api"
        endpoint = f"{base_url}/observacion/convencional/datos/estacion/{station_id}"
        
        # First request to get data URL
        response = requests.get(endpoint, params={"api_key": api_key})
        if response.status_code != 200:
            return None
            
        data_url = response.json().get('datos')
        if not data_url:
            return None
            
        # Second request to get actual data
        weather_data = requests.get(data_url).json()
        if not weather_data:
            return None
            
        # Get latest observation
        latest = weather_data[0] if weather_data else None
        if not latest:
            return None
            
        # Format weather data
        weather_info = {
            'temperatura': latest.get('ta', 'N/A'),
            'humedad': latest.get('hr', 'N/A'),
            'precipitacion': latest.get('prec', 'N/A'),
            'viento_velocidad': latest.get('vv', 'N/A'),
            'viento_direccion': latest.get('dv', 'N/A'),
            'presion': latest.get('pres', 'N/A'),
            'fecha_hora': latest.get('fint', 'N/A')
        }
        
        return weather_info
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return None

def display_station_weather(station_data, weather_data):
    """Display weather information for a station"""
    if not weather_data:
        st.warning("No hay datos meteorológicos disponibles")
        return
        
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Temperatura", 
            f"{weather_data['temperatura']}°C"
        )
        st.metric(
            "Presión", 
            f"{weather_data['presion']} hPa"
        )
        
    with col2:
        st.metric(
            "Humedad", 
            f"{weather_data['humedad']}%"
        )
        st.metric(
            "Precipitación", 
            f"{weather_data['precipitacion']} mm"
        )
        
    with col3:
        st.metric(
            "Velocidad Viento", 
            f"{weather_data['viento_velocidad']} km/h"
        )
        st.metric(
            "Dirección Viento", 
            f"{weather_data['viento_direccion']}°"
        )
    
    # Show last update time
    st.caption(f"Última actualización: {weather_data['fecha_hora']}")