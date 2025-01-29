import pandas as pd
import requests
from typing import List, Dict, Optional
from .base import BaseTransformer

class RaceScheduleTransformer(BaseTransformer):
    def transform(self, endpoint: str) -> pd.DataFrame:
        """Transform race schedule data from endpoint URL to DataFrame"""
        try:
            # Extract year from endpoint
            parts = endpoint.split('/')
            year = next(p for p in parts if p.isdigit())
            
            # Get race schedule
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()['MRData']['RaceTable']['Races']
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Extract nested Circuit information
            if 'Circuit' in df.columns:
                circuit_df = pd.json_normalize(df['Circuit'])
                df = df.drop('Circuit', axis=1)
                df = pd.concat([df, circuit_df], axis=1)
            
            # Add lap times endpoints for each race
            df['lap_endpoint'] = df.apply(
                lambda row: f"{self.BASE_URL}/{year}/{row['round']}/laps",
                axis=1
            )
            
            return df
            
        except Exception as e:
            print(f"Error processing race schedule: {str(e)}")
            return pd.DataFrame() 