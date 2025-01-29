import pandas as pd
import requests
import argparse
from typing import List, Dict, Optional
from .base import BaseTransformer

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

def process_standings(standings_lists, standing_type='driver'):
    """Process standings data into DataFrame"""
    rows = []
    for standings in standings_lists:
        season = standings.get('season', '')
        round_num = standings.get('round', '')
        
        for standing in standings.get('StandingsLists', []):
            if standing_type == 'driver':
                for driver_standing in standing.get('DriverStandings', []):
                    driver = driver_standing.get('Driver', {})
                    constructor = driver_standing.get('Constructors', [{}])[0]
                    rows.append({
                        'season': season,
                        'round': round_num,
                        'position': driver_standing.get('position', ''),
                        'points': driver_standing.get('points', ''),
                        'wins': driver_standing.get('wins', ''),
                        'driver_id': driver.get('driverId', ''),
                        'driver_code': driver.get('code', driver.get('driverId', ''))[:3].upper(),  # Fallback to ID
                        'driver_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
                        'constructor': constructor.get('name', '')
                    })
            else:  # constructor standings
                for const_standing in standing.get('ConstructorStandings', []):
                    constructor = const_standing.get('Constructor', {})
                    rows.append({
                        'season': season,
                        'round': round_num,
                        'position': const_standing.get('position', ''),
                        'points': const_standing.get('points', ''),
                        'wins': const_standing.get('wins', ''),
                        'constructor_id': constructor.get('constructorId', ''),
                        'constructor_name': constructor.get('name', ''),
                        'nationality': constructor.get('nationality', '')
                    })
    
    return pd.DataFrame(rows)

class StandingsTransformer(BaseTransformer):
    def transform(self, endpoint: str) -> pd.DataFrame:
        """Transform standings data from endpoint URL to DataFrame"""
        try:
            # Determine standings type from endpoint
            standing_type = 'driver' if 'driver' in endpoint.lower() else 'constructor'
            
            # Extract driver ID from URL if present
            driver_id = None
            if '/drivers/' in endpoint:
                driver_id = endpoint.split('/drivers/')[1].split('/')[0]
            
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()['MRData']['StandingsTable']
            
            # Get season from the data
            season = data.get('season', '')
            standings_lists = data.get('StandingsLists', [])
            
            if not standings_lists:
                return pd.DataFrame()
            
            rows = []
            for standing_list in standings_lists:
                if standing_type == 'driver':
                    for standing in standing_list.get('DriverStandings', []):
                        driver = standing.get('Driver', {})
                        constructor = standing.get('Constructors', [{}])[0]
                        
                        # Skip if not the requested driver
                        if driver_id and driver.get('driverId') != driver_id:
                            continue
                            
                        rows.append({
                            'season': season,
                            'round': standing_list.get('round', ''),
                            'position': int(standing.get('position', 0)),
                            'points': float(standing.get('points', 0)),
                            'wins': int(standing.get('wins', 0)),
                            'driver_id': driver.get('driverId', ''),
                            'driver_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
                            'constructor': constructor.get('name', '')
                        })
                else:  # constructor standings
                    for standing in standing_list.get('ConstructorStandings', []):
                        constructor = standing.get('Constructor', {})
                        rows.append({
                            'season': season,
                            'round': standing_list.get('round', ''),
                            'position': int(standing.get('position', 0)),
                            'points': float(standing.get('points', 0)),
                            'wins': int(standing.get('wins', 0)),
                            'constructor_id': constructor.get('constructorId', ''),
                            'constructor_name': constructor.get('name', ''),
                            'nationality': constructor.get('nationality', '')
                        })
            
            df = pd.DataFrame(rows)
            if not df.empty:
                df = df.sort_values(['season', 'position'])
            
            return df
            
        except Exception as e:
            print(f"Error processing standings data: {str(e)}")
            return pd.DataFrame()

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