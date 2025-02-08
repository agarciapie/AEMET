import plotly.express as px
import streamlit as st
import logging
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class APISession:
    _instance = None
    _cache = {}
    _last_request = 0
    _request_delay = 1  # Seconds between requests
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.setup_session()
        return cls._instance
    
    def setup_session(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
    def get(self, url, **kwargs):
        """Get with caching and rate limiting"""
        cache_key = url + str(kwargs)
        
        # Check cache
        if cache_key in self._cache:
            if time.time() - self._cache[cache_key]['timestamp'] < 3600:
                return self._cache[cache_key]['data']
        
        # Rate limiting
        now = time.time()
        if now - self._last_request < self._request_delay:
            time.sleep(self._request_delay)
        
        # Make request
        response = self.session.get(url, **kwargs)
        self._last_request = time.time()
        
        if response.status_code == 200:
            self._cache[cache_key] = {
                'data': response.json(),
                'timestamp': time.time()
            }
            return response.json()
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_with_retry(url, headers, params):
    """Fetch data with retry logic and caching"""
    api_session = APISession()
    try:
        with st.spinner('Fetching data...'):
            response = api_session.session.get(
                url, 
                headers=headers, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"API request failed: {str(e)}")
        return None

def create_weather_map(df):
    """Create weather stations map"""
    if df.empty:
        return None
        
    fig = px.scatter_mapbox(
        df,
        lat='latitud',
        lon='longitud',
        hover_name='nombre',
        hover_data=['provincia', 'altitud'],
        zoom=5,
        center={"lat": 40.4168, "lon": -3.7038},
        title="Estaciones Meteorológicas"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":30,"l":0,"b":0},
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    return fig