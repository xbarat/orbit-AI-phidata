import pandas as pd
import requests
import argparse

def fetch_qualifying_data(year: str, round_num: str = None):
    """Fetch qualifying data from Ergast API"""
    try:
        url = f"http://ergast.com/api/f1/{year}/{round_num}/qualifying.json" if round_num else f"http://ergast.com/api/f1/{year}/qualifying.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['MRData']['RaceTable']['Races']
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []
    except ValueError as e:
        print(f"Invalid JSON response: {e}")
        return []

def process_qualifying_data(races):
    """Process qualifying data into DataFrame"""
    rows = []
    for race in races:
        race_info = {
            'season': race['season'],
            'round': race['round'],
            'race_name': race['raceName'],
            'circuit_id': race['Circuit']['circuitId'],
            'circuit_name': race['Circuit']['circuitName'],
            'locality': race['Circuit']['Location'].get('locality'),
            'country': race['Circuit']['Location'].get('country')
        }
        
        for result in race['QualifyingResults']:
            driver = result['Driver']
            constructor = result['Constructor']
            
            rows.append({
                **race_info,
                'driver_id': driver['driverId'],
                'driver_name': f"{driver['givenName']} {driver['familyName']}",
                'constructor_id': constructor['constructorId'],
                'constructor_name': constructor['name'],
                'position': int(result['position']),
                'q1_time': result.get('Q1'),
                'q2_time': result.get('Q2'),
                'q3_time': result.get('Q3')
            })
    
    return pd.DataFrame(rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='F1 Qualifying Processor')
    parser.add_argument('--year', type=int, required=True, help='Season year')
    parser.add_argument('--round', type=int, required=False, default=None, help='Race round number (optional)')
    args = parser.parse_args()

    races = fetch_qualifying_data(str(args.year), str(args.round) if args.round else None)
    
    if races:
        df = process_qualifying_data(races)
        print(f"Successfully processed {len(df)} qualifying records")
        print(df.head())
        # df.to_csv(f"f1_qualifying_{args.year}_{args.round or 'all'}.csv", index=False)
    else:
        print("No data processed")

# Step 5: Display the DataFrame
print(df.head())
print(df.shape)

# Optional: Save to CSV
# df.to_csv("f1_2022_round1_qualifying.csv", index=False)
