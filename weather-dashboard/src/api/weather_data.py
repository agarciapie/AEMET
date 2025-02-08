import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

class WeatherData:
    """
    AEMET API client for fetching weather station data
    
    Attributes:
        api_key (str): AEMET API authentication key
        base_url (str): AEMET API base URL
    
    Methods:
        get_stations(): Fetches all weather stations
        _fetch_stations(api_key, base_url): Static method to fetch and cache station data
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://opendata.aemet.es/opendata/api"
    
    def get_stations(self):
        """Fetch all weather stations"""
        return self._fetch_stations(self.api_key, self.base_url)
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def _fetch_stations(api_key, base_url):
        """Cached method to fetch stations data"""
        endpoint = f"{base_url}/valores/climatologicos/inventarioestaciones/todasestaciones/"
        params = {"api_key": api_key}
        
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                data_url = response.json().get('datos')
                if data_url:
                    data = requests.get(data_url).json()
                    return pd.DataFrame(data)
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error fetching stations: {e}")
            return pd.DataFrame()