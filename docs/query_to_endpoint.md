# Query to Endpoint Component

## Overview
The Query-to-Endpoint component is a specialized system that converts natural language F1 queries into appropriate Ergast API endpoints. It uses a two-agent approach to systematically analyze queries and determine the minimal set of endpoints needed for data visualization.

## Design Philosophy
- **Systematic Analysis**: Break down queries into clear data requirements before selecting endpoints
- **Minimal Endpoints**: Only select endpoints that directly contribute to the visualization
- **Data-First Approach**: Focus on what data is needed before deciding how to fetch it

## Architecture

### 1. Understanding Agent
The first agent acts as a Formula 1 data analyst, breaking down queries into structured parameters:

- **Role**: Determines exact data points needed for visualization
- **Process**:
  1. Identifies specific subjects (drivers, constructors)
  2. Lists required metrics (wins, points, podiums)
  3. Calculates exact time periods
  4. Determines data granularity needed
  5. Considers visualization requirements

### 2. Endpoint Agent
The second agent acts as a Formula 1 data engineer, mapping data requirements to specific endpoints:

- **Role**: Selects minimal set of endpoints needed
- **Endpoint Selection Rules**:
  - `/driverStandings` for season-end totals
  - `/results` for race-by-race performance
  - `/qualifying` for qualifying data
  - `/laps` for timing data
  - `/pitstops` for pit stop analysis

### Data Models

#### QueryParameters
```python
{
    "action": "compare",
    "entity": "driver",
    "parameters": {"drivers": ["lewis_hamilton", "max_verstappen"]},
    "temporal": {"type": "range", "years": ["2021", "2022", "2023"]}
}
```

#### F1QueryResponse
```python
{
    "endpoints": [
        "http://ergast.com/api/f1/2023/driverStandings.json",
        "http://ergast.com/api/f1/2022/driverStandings.json"
    ],
    "explanation": "Need driver standings from 2022-2023 to compare performance"
}
```

## Example Flow

1. **Input Query**:
   ```
   "How does Lewis Hamilton compare to Charles Leclerc in terms of wins, podiums, and points over the last 5 seasons?"
   ```

2. **Understanding Agent Analysis**:
   - Subjects: Lewis Hamilton, Charles Leclerc
   - Metrics: wins, podiums, points
   - Time Period: 2019-2023
   - Granularity: Season totals needed

3. **Endpoint Selection**:
   - Uses `/driverStandings` endpoint for each year
   - Returns endpoints for 2019-2023

## Key Features

1. **Systematic Processing**:
   - Clear separation between understanding and endpoint selection
   - Structured parameter extraction
   - Systematic endpoint mapping

2. **Data-Centric Approach**:
   - Focuses on visualization requirements
   - Considers data structure needs
   - Minimizes API calls

3. **Flexibility**:
   - Handles various query types
   - Adapts to different data granularities
   - Supports multiple metrics and time periods

## Usage
```python
from backend.phi.query_to_endpoint import process_query

# Process a single query
endpoints = process_query("How does Lewis Hamilton compare to Charles Leclerc?")

# Test multiple queries
test_queries([0, 1, 2])  # Test queries by index
```

## Integration Points

- **Input**: Natural language queries about F1 data
- **Output**: List of Ergast API endpoints needed for visualization
- **Dependencies**: 
  - PHI framework for agent management
  - Pydantic for data validation
  - OpenAI for language processing 