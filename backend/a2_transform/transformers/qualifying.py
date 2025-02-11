import pandas as pd
import requests
from typing import List, Dict, Optional
from .base import BaseTransformer

class QualifyingTransformer(BaseTransformer):
    def transform(self, endpoint: str) -> pd.DataFrame:
        """Transform qualifying data from endpoint URL to DataFrame"""
        try:
            # Extract year from endpoint
            parts = endpoint.split('/')
            year = next(p for p in parts if p.isdigit())
            
            # Make API request
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()['MRData']
            
            # Process data based on response structure
            if 'RaceTable' in data:
                return self._process_race_table(data['RaceTable'])
            elif 'QualifyingTable' in data:
                return self._process_qualifying_table(data['QualifyingTable'])
            else:
                print(f"Unexpected data structure in response: {list(data.keys())}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error processing qualifying data: {str(e)}")
            return pd.DataFrame()

    def _process_race_table(self, race_table: Dict) -> pd.DataFrame:
        """Process data from RaceTable format"""
        rows = []
        for race in race_table.get('Races', []):
            race_info = {
                'season': race.get('season'),
                'round': race.get('round'),
                'race_name': race.get('raceName'),
                'circuit_id': race.get('Circuit', {}).get('circuitId'),
                'circuit_name': race.get('Circuit', {}).get('circuitName'),
                'date': race.get('date'),
            }
            
            for quali in race.get('QualifyingResults', []):
                driver = quali.get('Driver', {})
                constructor = quali.get('Constructor', {})
                
                rows.append({
                    **race_info,
                    'driver_id': driver.get('driverId'),
                    'driver_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                    'constructor_id': constructor.get('constructorId'),
                    'constructor_name': constructor.get('name'),
                    'position': quali.get('position'),
                    'q1_time': quali.get('Q1', ''),
                    'q2_time': quali.get('Q2', ''),
                    'q3_time': quali.get('Q3', '')
                })
        
        return pd.DataFrame(rows)

    def _process_qualifying_table(self, qualifying_table: Dict) -> pd.DataFrame:
        """Process data from QualifyingTable format"""
        rows = []
        for quali in qualifying_table.get('QualifyingResults', []):
            driver = quali.get('Driver', {})
            constructor = quali.get('Constructor', {})
            
            rows.append({
                'season': qualifying_table.get('season'),
                'round': qualifying_table.get('round'),
                'driver_id': driver.get('driverId'),
                'driver_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                'constructor_id': constructor.get('constructorId'),
                'constructor_name': constructor.get('name'),
                'position': quali.get('position'),
                'q1_time': quali.get('Q1', ''),
                'q2_time': quali.get('Q2', ''),
                'q3_time': quali.get('Q3', '')
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
