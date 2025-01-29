# transform_status.py

import pandas as pd
import requests
import argparse
from typing import Optional

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

class StatusTransformer:
    def transform(self, endpoint: str) -> pd.DataFrame:
        """Transform status data from endpoint URL to DataFrame"""
        # Extract parameters from endpoint
        parts = endpoint.split('/')
        year = parts[5]
        
        if 'laps' in endpoint:
            if len(parts) > 8 and parts[8].endswith('.json'):
                lap_number = parts[8].replace('.json', '')
                round_num = parts[6]
                return self._process_laps(year, round_num, lap_number)
            else:
                # Handle all laps case
                round_num = parts[6]
                return self._process_all_laps(year, round_num)
        else:
            # Handle status endpoint
            round_num = parts[6]
            return self._process_status(year, round_num)

    def _process_laps(self, year: str, round_num: str, lap_number: str) -> pd.DataFrame:
        """Process specific lap data"""
        race_data = fetch_lap_timings(year, round_num, lap_number)
        return process_lap_timings(race_data)

    def _process_all_laps(self, year: str, round_num: str) -> pd.DataFrame:
        """Process all laps data"""
        try:
            url = f"http://ergast.com/api/f1/{year}/{round_num}/laps.json"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            races = data['MRData']['RaceTable']['Races']
            if not races:
                return pd.DataFrame()
            
            all_laps_data = []
            for race in races:
                for lap in race['Laps']:
                    lap_data = {**race}  # Copy race info
                    lap_data['Laps'] = [lap]  # Replace with single lap
                    all_laps_data.append(process_lap_timings(lap_data))
            
            return pd.concat(all_laps_data, ignore_index=True) if all_laps_data else pd.DataFrame()
        except Exception as e:
            print(f"Error processing all laps: {e}")
            return pd.DataFrame()

    def _process_status(self, year: str, round_num: str) -> pd.DataFrame:
        """Process race status data"""
        try:
            url = f"http://ergast.com/api/f1/{year}/{round_num}/status.json"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            races = data['MRData']['RaceTable']['Races']
            if not races:
                return pd.DataFrame()

            rows = []
            for race in races:
                circuit_info = race['Circuit']
                for result in race['Results']:
                    rows.append({
                        'season': race['season'],
                        'round': race['round'],
                        'race_name': race['raceName'],
                        'circuit_id': circuit_info['circuitId'],
                        'circuit_name': circuit_info['circuitName'],
                        'driver_id': result['Driver']['driverId'],
                        'driver_name': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                        'constructor_id': result['Constructor']['constructorId'],
                        'status': result['status'],
                        'position': int(result['position']) if 'position' in result else None,
                        'laps_completed': int(result['laps']) if 'laps' in result else None
                    })
            return pd.DataFrame(rows)
        except Exception as e:
            print(f"Error processing status: {e}")
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