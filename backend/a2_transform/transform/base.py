import logging
import pandas as pd
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs
import functools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransformerError(Exception):
    """Base exception for transformation errors"""
    pass

def safe_transform(func):
    """Decorator for error handling in transformers"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Transform error in {func.__name__}: {str(e)}")
            return pd.DataFrame()
    return wrapper

class BaseTransformer:
    """Base class for all F1 data transformers"""
    
    @staticmethod
    def parse_endpoint_params(endpoint: str) -> Dict:
        """Extract parameters from endpoint URL"""
        parsed = urlparse(endpoint)
        params = parse_qs(parsed.query)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        # Default parameter extraction
        result = {
            'year': None,
            'round_num': None,
            'driver': params.get('driver', [None])[0],
            'circuit': params.get('circuitId', [None])[0]
        }
        
        # Extract year and round from path
        for i, part in enumerate(path_parts):
            if part == 'f1' and i + 1 < len(path_parts):
                result['year'] = path_parts[i + 1]
                if i + 2 < len(path_parts) and path_parts[i + 2].isdigit():
                    result['round_num'] = path_parts[i + 2]
        
        return result
    
    @safe_transform
    def fetch_and_transform(self, endpoint: str) -> pd.DataFrame:
        """Universal entry point for transformers"""
        params = self.parse_endpoint_params(endpoint)
        raw_data = self.fetch_data(params)
        return self.process_data(raw_data, params)
    
    def fetch_data(self, params: Dict) -> Dict:
        """Fetch data from Ergast API"""
        raise NotImplementedError("Subclasses must implement fetch_data")
    
    def process_data(self, raw_data: Dict, params: Dict) -> pd.DataFrame:
        """Process raw API data into DataFrame"""
        raise NotImplementedError("Subclasses must implement process_data") 