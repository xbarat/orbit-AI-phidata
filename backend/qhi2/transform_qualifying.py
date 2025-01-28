import pandas as pd
import requests

# Step 1: Fetch the API response
url = "http://ergast.com/api/f1/2022/1/qualifying.json"
response = requests.get(url)
data = response.json()

# Step 2: Extract relevant sections
races = data['MRData']['RaceTable']['Races']

# Step 3: Flatten data and construct rows
rows = []
for race in races:
    race_name = race['raceName']
    season = race['season']
    round_number = race['round']
    circuit_id = race['Circuit']['circuitId']
    circuit_name = race['Circuit']['circuitName']
    location = race['Circuit']['Location']
    locality = location.get('locality')
    country = location.get('country')

    for result in race['QualifyingResults']:
        driver = result['Driver']
        constructor = result['Constructor']
        
        # Extract qualifying times
        q1_time = result.get('Q1', None)
        q2_time = result.get('Q2', None)
        q3_time = result.get('Q3', None)
        
        # Construct a row
        rows.append({
            'season': season,
            'round': round_number,
            'race_name': race_name,
            'circuit_id': circuit_id,
            'circuit_name': circuit_name,
            'locality': locality,
            'country': country,
            'driver_id': driver['driverId'],
            'driver_name': f"{driver['givenName']} {driver['familyName']}",
            'constructor_id': constructor['constructorId'],
            'constructor_name': constructor['name'],
            'position': int(result['position']),
            'q1_time': q1_time,
            'q2_time': q2_time,
            'q3_time': q3_time
        })

# Step 4: Create the DataFrame
df = pd.DataFrame(rows)

# Step 5: Display the DataFrame
print(df.head())
print(df.shape)

# Optional: Save to CSV
# df.to_csv("f1_2022_round1_qualifying.csv", index=False)
