import pandas as pd
import requests
import argparse

def fetch_race_results(year, round_num=None):
    """Fetch race results with optional round parameter"""
    try:
        # Build URL based on round presence
        if round_num:
            url = f"http://ergast.com/api/f1/{year}/{round_num}/results.json"
        else:
            url = f"http://ergast.com/api/f1/{year}/results.json"
            
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['MRData']['RaceTable']['Races']
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []
    except (KeyError, ValueError) as e:
        print(f"Data processing error: {e}")
        return []

def process_results_data(races):
    """Process race data into DataFrame"""
    rows = []
    for race in races:
        race_info = {
            'race_id': race.get('round'),
            'season': race.get('season'),
            'race_name': race.get('raceName'),
            'circuit_id': race.get('Circuit', {}).get('circuitId'),
            'date': race.get('Date'),
            'time': race.get('Time')
        }
        
        for result in race.get('Results', []):
            driver = result.get('Driver', {})
            constructor = result.get('Constructor', {})
            
            rows.append({
                **race_info,
                'driver_id': driver.get('driverId'),
                'driver_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                'constructor_id': constructor.get('constructorId'),
                'constructor_name': constructor.get('name'),
                'grid': try_int(result.get('grid')),
                'laps': try_int(result.get('laps')),
                'position': try_int(result.get('position')),
                'status': result.get('status'),
                'points': float(result.get('points', 0))
            })
    
    return pd.DataFrame(rows)

def try_int(value):
    """Safe conversion to integer"""
    try:
        return int(value) if value and str(value).isdigit() else None
    except:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='F1 Results Processor')
    parser.add_argument('--year', type=int, required=True, help='Season year')
    parser.add_argument('--round', type=int, required=False, default=None, help='Race round number (optional)')
    args = parser.parse_args()

    races_data = fetch_race_results(args.year, args.round)
    
    if races_data:
        df = process_results_data(races_data)
        print(f"Successfully processed {len(df)} results")
        print(df.head())
        # df.to_csv(f"f1_results_{args.year}_{args.round or 'all'}.csv", index=False)
    else:
        print("No data processed")
