# F1 Data Query Pipeline

A natural language interface for querying Formula 1 race data using the Ergast API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key in a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

The pipeline can be run in three different modes:

### 1. Demo Mode
Run a set of example queries to showcase different capabilities:
```bash
python backend/main.py --demo
```

### 2. Single Query Mode
Process a specific query from the command line:
```bash
python backend/main.py --query "Show me Lewis Hamilton's race results from 2023"
```

### 3. Interactive Mode
Start an interactive session where you can enter multiple queries:
```bash
python backend/main.py
```

### 4. Streamlit Web Interface
Run the web interface for an interactive experience:
```bash
streamlit run frontend/app.py
```

## Example Queries

- "Show me Lewis Hamilton's race results from 2023"
- "Compare Max Verstappen and Sergio Perez's performance in 2023"
- "Get the qualifying results for the 2023 Monaco Grand Prix"
- "Show me the driver standings after each race in 2023"

## Features

- Natural language query processing
- Rich console output with formatted tables
- Basic data analysis and statistics
- Support for multiple F1 data types:
  - Race results
  - Driver standings
  - Qualifying results
  - Lap times and status

## Error Handling

The pipeline includes comprehensive error handling:
- Invalid queries
- API connection issues
- Data processing errors

All errors are logged with detailed information for debugging. 