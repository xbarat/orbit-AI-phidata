import pandas as pd
import requests
import argparse

def fetch_standings(year: str, standing_type: str):
    """Fetch standings data from Ergast API"""
    try:
        url = f"http://ergast.com/api/f1/{year}/{standing_type}Standings.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['MRData']['StandingsTable']['StandingsLists']
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []
    except ValueError as e:
        print(f"Invalid JSON response: {e}")
        return []

def process_standings(standings_lists, standing_type: str):
    """Process standings data into DataFrame"""
    if not standings_lists:
        return pd.DataFrame()

    standings = standings_lists[0]
    season = standings['season']
    round_number = standings['round']
    rows = []

    for standing in standings.get(f'{standing_type.capitalize()}Standings', []):
        row = {
            'season': season,
            'round': round_number,
            'position': int(standing['position']),
            'points': float(standing['points']),
            'wins': int(standing['wins']),
            'standing_type': standing_type
        }

        if standing_type == 'driver':
            driver = standing['Driver']
            constructor = standing['Constructors'][-1]
            row.update({
                'driver_id': driver['driverId'],
                'driver_name': f"{driver['givenName']} {driver['familyName']}",
                'driver_code': driver['code'],
                'constructor_id': constructor['constructorId'],
                'constructor_name': constructor['name'],
                'nationality_driver': driver['nationality'],
                'nationality_constructor': constructor['nationality']
            })
        else:
            constructor = standing['Constructor']
            row.update({
                'constructor_id': constructor['constructorId'],
                'constructor_name': constructor['name'],
                'nationality_constructor': constructor['nationality']
            })
        
        rows.append(row)
    
    return pd.DataFrame(rows)

class StandingsTransformer:
    def transform(self, endpoint: str) -> pd.DataFrame:
        """Transform standings data from endpoint URL to DataFrame"""
        # Extract parameters from endpoint
        parts = endpoint.split('/')
        year = parts[5]
        standing_type = 'driver' if 'driverStandings' in endpoint else 'constructor'
        
        # Fetch and process data
        standings_lists = fetch_standings(year, standing_type)
        return process_standings(standings_lists, standing_type)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='F1 Standings Processor')
    parser.add_argument('--year', type=int, required=True, help='Season year')
    parser.add_argument('--type', choices=['driver', 'constructor', 'both'], default='both', help='Type of standings to fetch')
    args = parser.parse_args()

    dfs = []

    if args.type in ['driver', 'both']:
        standings_lists = fetch_standings(str(args.year), 'driver')
        df = process_standings(standings_lists, 'driver')
        if not df.empty:
            dfs.append(df)
            print(f"Successfully processed {len(df)} driver standings")

    if args.type in ['constructor', 'both']:
        standings_lists = fetch_standings(str(args.year), 'constructor')
        df = process_standings(standings_lists, 'constructor')
        if not df.empty:
            dfs.append(df)
            print(f"Successfully processed {len(df)} constructor standings")

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        print("\nCombined standings:")
        print(combined_df.head())
        # combined_df.to_csv(f"f1_standings_{args.year}_{args.type}.csv", index=False)
    else:
        print("No data processed")