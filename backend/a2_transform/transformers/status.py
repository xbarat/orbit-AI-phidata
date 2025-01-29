# transform_status.py

import pandas as pd
import requests
import argparse
from typing import Optional
from .base import BaseTransformer

def fetch_lap_timings(year: str, round_num: str, lap_number: str):
    """Fetch lap timing data from Ergast API"""
    try:
        url = f"http://ergast.com/api/f1/{year}/{round_num}/laps/{lap_number}.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['MRData']['RaceTable']['Races'][0]
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except ValueError as e:
        print(f"Invalid JSON response: {e}")
        return None

def process_lap_timings(race_data):
    """Process lap timing data into DataFrame"""
    if not race_data:
        return pd.DataFrame()

    rows = []
    circuit_info = race_data['Circuit']
    location_info = circuit_info['Location']

    for lap in race_data['Laps']:
        lap_number = lap['number']
        for timing in lap['Timings']:
            rows.append({
                'season': race_data['season'],
                'round': race_data['round'],
                'lap_number': int(lap_number),
                'driver_id': timing['driverId'],
                'position': int(timing['position']),
                'time': timing['time'],
                'circuit_id': circuit_info['circuitId'],
                'circuit_name': circuit_info['circuitName'],
                'locality': location_info['locality'],
                'country': location_info['country'],
                'race_date': race_data['date'],
                'race_time': race_data['time']
            })

    return pd.DataFrame(rows)

class StatusTransformer(BaseTransformer):
    def transform(self, endpoint: str) -> pd.DataFrame:
        """Transform status data from endpoint URL to DataFrame"""
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()['MRData']['StatusTable']
            
            # Get season from the data
            season = data.get('season', '')
            
            # Get status data
            status_data = data.get('Status', [])
            if not status_data:
                return pd.DataFrame()
            
            rows = []
            for status in status_data:
                rows.append({
                    'season': season,
                    'status_id': status.get('statusId', ''),
                    'status': status.get('status', ''),
                    'count': int(status.get('count', 0))
                })
            
            df = pd.DataFrame(rows)
            
            if not df.empty:
                # Filter for DNF-related statuses if needed
                dnf_keywords = ['Accident', 'Mechanical', 'Engine', 'Gearbox', 'Retired', 'DNF', 'Collision']
                df['is_dnf'] = df['status'].str.contains('|'.join(dnf_keywords), case=False)
                
                # Add summary stats
                df['total_races'] = df['count'].sum()
                df['dnf_rate'] = df[df['is_dnf']]['count'].sum() / df['total_races']
                
                # Sort by count
                df = df.sort_values('count', ascending=False)
            
            return df
            
        except Exception as e:
            print(f"Error processing status: {str(e)}")
            return pd.DataFrame()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='F1 Status Processor')
    parser.add_argument('--year', type=int, required=True, help='Season year')
    parser.add_argument('--round', type=int, required=True, help='Race round number')
    parser.add_argument('--lap', type=int, required=True, help='Lap number')
    args = parser.parse_args()

    race_data = fetch_lap_timings(str(args.year), str(args.round), str(args.lap))
    
    if race_data:
        df = process_lap_timings(race_data)
        print(f"Successfully processed {len(df)} lap timing records")
        print(df.head())
        # df.to_csv(f"f1_laptimes_{args.year}_{args.round}_lap{args.lap}.csv", index=False)
    else:
        print("No data processed")