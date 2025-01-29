# transform_status.py

import pandas as pd
import requests
import argparse

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