from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from phi.agent import Agent
from a1_query.model.openai import OpenAIChat
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
    """Create an agent that understands what data is needed for visualization"""
    return Agent(
        model=openai,
        description="You are a Formula 1 data analyst who determines exactly what data points are needed for visualization",
        output_model=QueryParameters,
        instructions=[
            "First identify the exact subjects (e.g., specific drivers, constructors, circuits)",
            "Then list the precise metrics needed (e.g., wins, points, podiums, laps, pitstops, finishing status)",
            "Calculate exact time periods (e.g., 'last 5 seasons' = 2019-2023)",
            "Format all identifiers as lowercase with underscores (e.g., lewis_hamilton)",
            "Think about the data structure needed for visualization (e.g., time series of points)",
            "Consider what granularity of data is needed (season totals vs race-by-race)",
            "Identify if we need cumulative stats or individual race results"
        ]
    )

def create_endpoint_agent():
    """Create an agent that maps parameters to Ergast API endpoints"""
    return Agent(
        model=openai,
        description="You are a Formula 1 data engineer who picks the minimal set of endpoints needed",
        output_model=F1QueryResponse,
        instructions=[
            "Pick endpoints based on data granularity needed:",
            "- Use /driverStandings for season-end totals (wins, points, position)",
            "- Use /results for race-by-race performance",
            "- Use /qualifying for qualifying performance",
            "- Use /circuits for circuit data",
            "- Use /laps for lap time data",
            "- Use /pitstops for pit stop data",
            "- Use /finishingStatus for finishing status data",
            "Always format URLs with:",
            "- .json suffix",
            "- Correct year parameter",
            "- Proper driver/constructor IDs",
            "Only select endpoints that directly contribute to the visualization",
            "Explain exactly how each endpoint's data will be used"
        ]
    )

def process_query(query: str) -> List[str]:
    """Process an F1 query and return relevant Ergast API endpoint URLs"""
    try:
        # Step 1: Extract structured parameters
        understanding_agent = create_understanding_agent()
        params_response = understanding_agent.run(f"""
        As a Formula 1 data analyst, determine exactly what data points we need:
        "{query}"
        
        Break down systematically:
        1. Subjects: Which specific drivers/constructors?
        2. Metrics: What exact statistics are needed?
        3. Time Period: Which specific years?
        4. Granularity: Do we need season totals or race-by-race data?
        5. Visualization: What data structure would we need to create the visualization?
        """)
        
        # Step 2: Map to endpoints
        endpoint_agent = create_endpoint_agent()
        result_response = endpoint_agent.run(f"""
        Based on these data requirements, select the minimal set of endpoints needed:
        {params_response.content.model_dump_json()}
        
        Core endpoints and their data:
        1. /driverStandings - Season-end totals (wins, points, position)
        2. /results - Individual race results
        3. /qualifying - Qualifying performance
        4. /laps - Lap time data
        5. /pitstops - Pit stop data
        
        Remember:
        - Only select endpoints that directly provide needed data
        - Format: http://ergast.com/api/f1/{{year}}/[endpoint].json
        - Add parameters only if needed (e.g., driver, round)
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