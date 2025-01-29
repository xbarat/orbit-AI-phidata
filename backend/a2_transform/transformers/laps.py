import pandas as pd
import requests
from typing import List, Dict, Optional
from .base import BaseTransformer

class LapTimesTransformer(BaseTransformer):
    def transform(self, endpoint: str) -> pd.DataFrame:
        """Transform lap times data focusing on fastest laps"""
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()['MRData']['RaceTable']
            
            if not data.get('Races'):
                print(f"No race data found for {endpoint}")
                return pd.DataFrame()
            
            race = data['Races'][0]
            
            # Extract fastest lap per driver
            driver_fastest_laps = {}
            for lap in race.get('Laps', []):
                for timing in lap['Timings']:
                    lap_time_sec = self._convert_lap_time_to_seconds(timing['time'])
                    driver_id = timing['driverId']
                    
                    if driver_id not in driver_fastest_laps or lap_time_sec < driver_fastest_laps[driver_id]['time']:
                        driver_fastest_laps[driver_id] = {
                            'time': lap_time_sec,
                            'lap_number': lap['number']
                        }
            
            # Create DataFrame
            rows = []
            for driver_id, lap_data in driver_fastest_laps.items():
                rows.append({
                    'season': race['season'],
                    'round': race['round'],
                    'race_name': race['raceName'],
                    'circuit_name': race['Circuit']['circuitName'],
                    'driver_id': driver_id,
                    'fastest_lap_time': lap_data['time'],
                    'fastest_lap_number': lap_data['lap_number']
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            print(f"Error processing lap times: {str(e)}")
            return pd.DataFrame()

    def _convert_lap_time_to_seconds(self, lap_time: str) -> float:
        """Convert lap time string (1:30.100) to seconds (90.100)"""
        try:
            if ':' in lap_time:
                minutes, seconds = lap_time.split(':')
                return float(minutes) * 60 + float(seconds)
            return float(lap_time)
        except:
            return 0.0

    def combine_results(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        """Combine results from multiple races"""
        if not dfs:
            return pd.DataFrame()
        
        # Combine all race summaries
        combined_df = pd.concat(dfs, ignore_index=True)
        
        if not combined_df.empty:
            # Sort by round number
            combined_df = combined_df.sort_values('round')
            
            # Add season summary
            season_summary = pd.DataFrame([{
                'round': 'Season Avg',
                'race_name': 'Full Season',
                'circuit_name': 'All Circuits',
                'date': combined_df['date'].max(),
                'total_laps': combined_df['total_laps'].sum(),
                'avg_lap_time': combined_df['avg_lap_time'].mean(),
                'std_lap_time': combined_df['std_lap_time'].mean(),
                'fastest_lap': combined_df['fastest_lap'].min(),
                'slowest_lap': combined_df['slowest_lap'].max(),
                'avg_position': combined_df['avg_position'].mean()
            }])
            
            # Append season summary to race-by-race data
            combined_df = pd.concat([combined_df, season_summary], ignore_index=True)
        
        return combined_df.round(3) 