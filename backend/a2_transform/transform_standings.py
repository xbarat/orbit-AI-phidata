import pandas as pd
import requests

def fetch_and_process_standings(standing_type):
    """Fetch and process standings data for either drivers or constructors"""
    try:
        url = f"http://ergast.com/api/f1/2022/1/{standing_type}Standings.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {standing_type}: {e}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"Invalid JSON response for {standing_type}: {e}")
        return pd.DataFrame()

    standings_list = data['MRData']['StandingsTable']['StandingsLists']
    season = data['MRData']['StandingsTable']['season']
    round_number = data['MRData']['StandingsTable']['round']

    rows = []
    for standing in standings_list[0].get(f'{standing_type.capitalize()}Standings', []):
        row = {
            'season': season,
            'round': round_number,
            'position': int(standing.get('position', 0)),
            'points': float(standing.get('points', 0)),
            'wins': int(standing.get('wins', 0)),
            'standing_type': standing_type
        }

        if standing_type == 'driver':
            driver = standing.get('Driver', {})
            constructor = standing.get('Constructors', [{}])[-1]
            row.update({
                'driver_id': driver.get('driverId'),
                'driver_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                'driver_code': driver.get('code'),
                'constructor_id': constructor.get('constructorId'),
                'constructor_name': constructor.get('name'),
                'nationality_driver': driver.get('nationality'),
                'nationality_constructor': constructor.get('nationality')
            })
        else:
            constructor = standing.get('Constructor', {})
            row.update({
                'driver_id': None,
                'driver_name': None,
                'driver_code': None,
                'constructor_id': constructor.get('constructorId'),
                'constructor_name': constructor.get('name'),
                'nationality_driver': None,
                'nationality_constructor': constructor.get('nationality')
            })
            
        rows.append(row)
    
    return pd.DataFrame(rows)

# Process both standings types and combine
driver_df = fetch_and_process_standings('driver')
constructor_df = fetch_and_process_standings('constructor')
combined_df = pd.concat([driver_df, constructor_df], ignore_index=True)

# Display and save the combined results
print(combined_df.head())
#combined_df.to_csv("combined_standings.csv", index=False)

# main
if __name__ == "__main__":
    driver_df = fetch_and_process_standings('driver')
    constructor_df = fetch_and_process_standings('constructor')
    combined_df = pd.concat([driver_df, constructor_df], ignore_index=True)
    print(combined_df.head())