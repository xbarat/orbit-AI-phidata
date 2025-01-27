import pandas as pd
import requests

# Step 1: Fetch the API response
url = "http://ergast.com/api/f1/2019/1/results.json"
response = requests.get(url)
data = response.json()

# Step 2: Extract relevant sections
races = data['MRData']['RaceTable']['Races']

# Step 3: Flatten data and construct rows
rows = []
for race in races:
    race_id = race['round']
    season = race['season']
    race_name = race['raceName']
    circuit_id = race['Circuit']['circuitId']
    
    for result in race['Results']:
        driver_id = result['Driver']['driverId']
        driver_name = f"{result['Driver']['givenName']} {result['Driver']['familyName']}"
        constructor_id = result['Constructor']['constructorId']
        constructor_name = result['Constructor']['name']
        grid = result.get('grid', None)
        laps = result.get('laps', None)
        position = result.get('position', None)
        status = result.get('status', None)
        
        rows.append({
            'race_id': race_id,
            'season': season,
            'race_name': race_name,
            'circuit_id': circuit_id,
            'driver_id': driver_id,
            'driver_name': driver_name,
            'constructor_id': constructor_id,
            'constructor_name': constructor_name,
            'grid': int(grid) if grid.isdigit() else None,
            'laps': int(laps) if laps.isdigit() else None,
            'position': int(position) if position.isdigit() else None,
            'status': status,
        })

# Step 4: Create the DataFrame
df = pd.DataFrame(rows)

# Step 5: Display the DataFrame
print(df.head())
# Print total shape
print(df.shape)

# Save to CSV (optional)
#df.to_csv("f1_results_2019.csv", index=False)
