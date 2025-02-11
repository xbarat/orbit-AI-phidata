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
            'date': race.get('date'),
            'time': race.get('time')
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

class RaceResultsTransformer:
    def transform(self, endpoint: str) -> pd.DataFrame:
        try:
            # Extract parameters
            parts = endpoint.split('/')
            if 'circuits' in parts:
                # Handle circuit-specific pattern: /f1/circuits/{circuitId}/{year}/results.json
                circuit_idx = parts.index('circuits') + 1
                year_idx = circuit_idx + 1
                if year_idx >= len(parts):
                    print(f"Invalid circuit endpoint: {endpoint}")
                    return pd.DataFrame()
                    
                circuit_id = parts[circuit_idx]
                year = parts[year_idx]
                return self._process_circuit_results(circuit_id, year)
                
            else:
                # Standard driver/year processing
                return self._process_driver_results(endpoint)
                
        except Exception as e:
            print(f"Error processing {endpoint}: {str(e)}")
            return pd.DataFrame()

    def _process_circuit_results(self, circuit_id: str, year: str):
        # First get all races at this circuit
        races = self._fetch_circuit_races(circuit_id, year)
        
        # Then get results for each race
        all_results = []
        for race in races:
            race_year = race['season']
            round_num = race['round']
            results = self._fetch_race_results(race_year, round_num)
            all_results.extend(self._process_results(results))
            
        return pd.DataFrame(all_results)

    def _process_driver_results(self, endpoint: str) -> pd.DataFrame:
        # Extract parameters from endpoint URL
        parts = endpoint.split('/')
        year = parts[5]
        round_num = parts[6] if len(parts) > 6 and not parts[6].startswith('drivers') else None
        
        # Fetch and process data
        races = fetch_race_results(year, round_num)
        return process_results_data(races)

    def _fetch_circuit_races(self, circuit_id: str, year: str):
        # Implement the logic to fetch races at a specific circuit and year
        # This is a placeholder and should be replaced with the actual implementation
        return []

    def _process_results(self, results):
        # Implement the logic to process results and return a list of dictionaries
        # This is a placeholder and should be replaced with the actual implementation
        return []

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
