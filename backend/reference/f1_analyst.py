from phi.agent import Agent
from a1_query.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
import os
from dotenv import load_dotenv
import pandas as pd
import fastf1
import numpy as np

# Load environment variables
load_dotenv()

# Configure FastF1
fastf1.Cache.enable_cache('cache')  # Cache race data locally

class F1Tools:
    """Custom tools for F1 data analysis"""
    
    def get_race_results(self, year: int, grand_prix: str) -> pd.DataFrame:
        """Get race results for a specific Grand Prix"""
        session = fastf1.get_session(year, grand_prix, 'R')
        session.load()
        return session.results[['Driver', 'Position', 'Points', 'Status']]
    
    def get_driver_lap_times(self, year: int, grand_prix: str, driver: str) -> pd.DataFrame:
        """Get lap times for a specific driver in a race"""
        session = fastf1.get_session(year, grand_prix, 'R')
        session.load()
        laps = session.laps.pick_driver(driver)
        return laps[['LapNumber', 'LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']]
    
    def get_qualifying_results(self, year: int, grand_prix: str) -> pd.DataFrame:
        """Get qualifying results for a specific Grand Prix"""
        session = fastf1.get_session(year, grand_prix, 'Q')
        session.load()
        return session.results[['Driver', 'Q1', 'Q2', 'Q3']]

def create_f1_analyst():
    return Agent(
        name="F1 Analyst",
        role="Formula 1 Data Analyst",
        model=OpenAIChat(api_key=os.getenv('OPENAI_API_KEY')),
        tools=[
            F1Tools(),
            DuckDuckGo()  # For getting latest news and context
        ],
        instructions=[
            "Always return data in pandas DataFrame format when possible",
            "Include statistical analysis when relevant",
            "Cite sources for non-statistical information",
            "Provide insights along with the data"
        ],
        show_tool_calls=True,
        markdown=True,
    )

def create_f1_team_analyst(f1_agent):
    return Agent(
        team=[f1_agent],
        instructions=[
            "Combine statistical analysis with contextual information",
            "Focus on performance trends and patterns",
            "Highlight key insights and anomalies",
            "Present data in both tabular and narrative formats"
        ],
        show_tool_calls=True,
        markdown=True,
    )

if __name__ == "__main__":
    # Create test queries
    test_queries = [
        "Compare the qualifying performance of Max Verstappen and Lewis Hamilton in the 2023 Monaco GP",
        "Analyze the race pace and tire degradation for Charles Leclerc in the 2023 British GP",
        "What were the key factors in Red Bull's dominance in the 2023 season?",
        "Create a performance comparison dataframe for the top 3 teams in the 2023 season",
    ]
    
    # Initialize agents
    f1_agent = create_f1_analyst()
    team_analyst = create_f1_team_analyst(f1_agent)
    
    # Test queries
    print("\n=== Testing F1 Analysis Capabilities ===")
    for query in test_queries:
        print(f"\nQuery: {query}")
        team_analyst.print_response(query, stream=True) 