# transform_status.py

import pandas as pd
import requests

def fetch_and_process_status():
    url = "http://ergast.com/api/f1/2022/1/laps/2.json"
    response = requests.get(url)
    data = response.json()
    return data

def fetch_and_process_lap_timings(year, round_num, lap_number):
    """Fetch and process lap timing data from Ergast API"""
    try:
        url = f"http://ergast.com/api/f1/{year}/{round_num}/laps/{lap_number}.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"Invalid JSON response: {e}")
        return pd.DataFrame()

    # Extract base race information
    race_table = data['MRData']['RaceTable']
    race_info = race_table['Races'][0]  # Access first race in list
    circuit_info = race_info['Circuit']
    location_info = circuit_info['Location']

    # Extract lap timings
    laps = race_info['Laps']  # Access laps directly
    rows = []

    for lap in laps:
        lap_number = lap['number']
        for timing in lap['Timings']:
            rows.append({
                'season': race_table['season'],
                'round': race_table['round'],
                'lap_number': int(lap_number),
                'driver_id': timing['driverId'],
                'position': int(timing['position']),
                'time': timing['time'],
                'circuit_id': circuit_info['circuitId'],
                'circuit_name': circuit_info['circuitName'],
                'locality': location_info['locality'],
                'country': location_info['country'],
                'race_date': race_info['date'],
                'race_time': race_info['time']
            })

    return pd.DataFrame(rows)

# Example usage
if __name__ == "__main__":
    # Test with Bahrain 2022 Lap 2 data
    df = fetch_and_process_lap_timings(2022, 1, 2)
    print(df.head())
    # df.to_csv("lap_timings_2022_1_2.csv", index=False)