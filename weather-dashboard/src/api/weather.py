import requests
import pandas as pd
import numpy as np
from functools import lru_cache

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZ2FyY2lhcGllQGdtYWlsLmNvbSIsImp0aSI6ImZiMTQxYWY0LTQ1MzMtNDc5NS1hNTM5LTM0Mjk4NzNjMGNlOSIsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzM4NTMwNjI0LCJ1c2VySWQiOiJmYjE0MWFmNC00NTMzLTQ3OTUtYTUzOS0zNDI5ODczYzBjZTkiLCJyb2xlIjoiIn0.GeKTxZLkTsGluLYZUjxZrMBG41K78-kq7b9JVHLF9I8"

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://opendata.aemet.es/opendata/api"
        self.session = requests.Session()
        
    @lru_cache(maxsize=32)
    def get_stations(self):
        """Get weather stations with caching"""
        endpoint = f"{self.base_url}/valores/climatologicos/inventarioestaciones/todasestaciones/"
        params = {"api_key": self.api_key}
        
        try:
            # Get data URL
            response = self.session.get(endpoint, params=params)
            if response.status_code == 200:
                data_url = response.json().get('datos')
                
                # Get actual data
                data_response = self.session.get(data_url)
                if data_response.status_code == 200:
                    return data_response.json()
        except Exception as e:
            print(f"API Error: {e}")
        return None

def process_weather_data(data):
    """Process and clean weather data"""
    if not data:
        return pd.DataFrame()
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Convert numeric columns
        numeric_cols = ['altitud', 'latitud', 'longitud']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Select and rename columns
        columns = {
            'nombre': 'nombre',
            'provincia': 'provincia',
            'altitud': 'altitud',
            'latitud': 'latitud',
            'longitud': 'longitud'
        }
        
        df = df[columns.keys()].rename(columns=columns)
        
        # Clean text columns
        df['nombre'] = df['nombre'].str.strip()
        df['provincia'] = df['provincia'].str.strip()
        
        # Remove rows with missing values
        df = df.dropna()
        
        return df
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return pd.DataFrame()