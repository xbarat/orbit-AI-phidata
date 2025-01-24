from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.model.openai import OpenAIChat
import os
from dotenv import load_dotenv
from query_index import query_index

# Load environment variables
load_dotenv()

# Get API key from environment variable
openai = OpenAIChat(api_key=os.getenv('OPENAI_API_KEY'))

class QueryParameters(BaseModel):
    """Parameters extracted from the query"""
    action: str = Field(description="Type of action: fetch, compare, analyze")
    entity: str = Field(description="Target entity: driver, constructor, race")
    parameters: Dict = Field(default_factory=dict, description="Extracted parameters like driver names, years")
    temporal: Optional[Dict] = Field(default=None, description="Temporal aspects like season ranges")

    model_config = {
        "json_schema_extra": {
            "example": {
                "action": "compare",
                "entity": "driver",
                "parameters": {"drivers": ["lewis_hamilton", "max_verstappen"]},
                "temporal": {"type": "range", "years": ["2021", "2022", "2023"]}
            }
        }
    }

class F1QueryResponse(BaseModel):
    """Final response with endpoints"""
    endpoints: List[str] = Field(default_factory=list, description="List of complete Ergast API URLs needed")
    explanation: str = Field(default="", description="Brief explanation of why these endpoints are needed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "endpoints": [
                    "http://ergast.com/api/f1/2023/driverStandings.json",
                    "http://ergast.com/api/f1/2022/driverStandings.json"
                ],
                "explanation": "Need driver standings from 2022-2023 to compare performance"
            }
        }
    }

def create_understanding_agent():
    """Create an agent that understands and extracts parameters from queries"""
    return Agent(
        model=openai,
        description="You are a Formula 1 data analyst who understands what data is needed to create visualizations and comparisons",
        output_model=QueryParameters,
        instructions=[
            "Think like a data analyst building a analytics dashboard",
            "For driver comparisons, consider what metrics need to be tracked (wins, points, podiums, etc.)",
            "For temporal analysis, determine the granularity needed (race-by-race, season totals, etc.)",
            "Consider what data structures would be needed to create meaningful visualizations",
            "Break down complex queries into required data points for comparison",
            "For 'last N seasons', calculate exact years (e.g., 'last 5' means 2019-2023)",
            "Format identifiers consistently (lowercase with underscores)",
            "Think about what standings/statistics are needed for a complete analysis"
        ]
    )

def create_endpoint_agent():
    """Create an agent that maps parameters to Ergast API endpoints"""
    return Agent(
        model=openai,
        description="You are a Formula 1 data engineer who knows exactly which endpoints provide the necessary data for analysis",
        output_model=F1QueryResponse,
        instructions=[
            "For driver comparisons, use driver standings endpoints to get championship positions and points",
            "When comparing specific metrics (wins, podiums), use driver standings for season totals",
            "For detailed race-by-race analysis, include race results endpoints",
            "Always include driver standings endpoints for overall performance metrics",
            "Use constructor standings when team performance is relevant",
            "Include qualifying results if race performance analysis is needed",
            "Always include .json suffix and limit=1000 for large datasets",
            "Explain why each endpoint is needed for the analysis",
            "Consider what data joins would be needed to create a complete analysis"
        ]
    )

def process_query(query: str) -> List[str]:
    """Process an F1 query and return relevant Ergast API endpoint URLs"""
    try:
        # Step 1: Extract structured parameters
        understanding_agent = create_understanding_agent()
        params_response = understanding_agent.run(f"""
        As a Formula 1 data analyst, analyze this query and determine what data we need:
        "{query}"
        
        Think about:
        - What metrics need to be compared (wins, points, podiums, etc.)
        - What granularity of data is needed (race-by-race, season totals)
        - What data structures would help visualize this comparison
        - What additional context might be needed for meaningful analysis
        - How to track performance trends over the specified time period
        """)
        
        # Step 2: Map to endpoints
        endpoint_agent = create_endpoint_agent()
        result_response = endpoint_agent.run(f"""
        Based on this analysis, determine which endpoints will provide the necessary data:
        {params_response.content.model_dump_json()}
        
        Available endpoints:
        1. Driver Standings: http://ergast.com/api/f1/{{year}}/driverStandings.json
        2. Constructor Standings: http://ergast.com/api/f1/{{year}}/constructorStandings.json
        3. Race Results: http://ergast.com/api/f1/{{year}}/{{round}}/results.json
        4. Driver Results: http://ergast.com/api/f1/drivers/{{driver}}/results.json
        5. Season Results: http://ergast.com/api/f1/{{year}}/results.json
        
        Remember:
        - Driver standings provide cumulative season statistics
        - Race results provide race-by-race performance data
        - Include all endpoints needed for a complete analysis
        - Consider what data will be needed for visualization
        """)
        
        # Output results
        print(f"\nQuery: {query}")
        print("Required Endpoints:")
        for url in result_response.content.endpoints:
            print(f"- {url}")
        print(f"Explanation: {result_response.content.explanation}")
        
        return result_response.content.endpoints
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return []

def test_queries(indices: List[int]):
    """Test the F1 query processor with query indices"""
    queries = query_index.get_queries(indices)
    for query in queries:
        process_query(query)

if __name__ == "__main__":
    test_queries([29]) 