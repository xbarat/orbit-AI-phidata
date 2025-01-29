import pandas as pd
import requests
from typing import Dict, List
from .base import BaseTransformer, safe_transform

class ResultsTransformer(BaseTransformer):
    """Transformer for F1 race results data"""
    
    def fetch_data(self, params: Dict) -> Dict:
        """Fetch race results with optional round parameter"""
        year = params['year']
        round_num = params['round_num']
        
        # Build URL based on parameters
        if round_num:
            url = f"http://ergast.com/api/f1/{year}/{round_num}/results.json"
        else:
            url = f"http://ergast.com/api/f1/{year}/results.json"
            
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['MRData']['RaceTable']['Races']
    
    def process_data(self, races: List[Dict], params: Dict) -> pd.DataFrame:
        """Process race data into DataFrame"""
        rows = []
        for race in races:
            race_info = {
                'race_id': race.get('round'),
                'season': race.get('season'),
                'race_name': race.get('raceName'),
                'circuit_id': race.get('Circuit', {}).get('circuitId'),
                'date': race.get('date'),
                'time': race.get('time')
            }
            
            for result in race.get('Results', []):
                driver = result.get('Driver', {})
                constructor = result.get('Constructor', {})
                
                # Filter by driver if specified
                if params.get('driver') and driver.get('driverId') != params['driver']:
                    continue
                
                rows.append({
                    **race_info,
                    'driver_id': driver.get('driverId'),
                    'driver_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                    'constructor_id': constructor.get('constructorId'),
                    'constructor_name': constructor.get('name'),
                    'grid': self._try_int(result.get('grid')),
                    'laps': self._try_int(result.get('laps')),
                    'position': self._try_int(result.get('position')),
                    'status': result.get('status'),
                    'points': float(result.get('points', 0))
                })
        
        return pd.DataFrame(rows)
    
    @staticmethod
    def _try_int(value):
        """Safe conversion to integer"""
        try:
            return int(value) if value and str(value).isdigit() else None
        except:
            return None 