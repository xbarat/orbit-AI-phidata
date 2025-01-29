from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.model.openai import OpenAIChat
import os
from dotenv import load_dotenv
from query_index import query_index
import pandas as pd
import uuid

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

class EndpointProcessingRequest(BaseModel):
    """Request for processing endpoints through transformers"""
    endpoints: List[str] = Field(..., description="List of Ergast API URLs to process")
    output_format: str = Field(default="dataframe", description="Output format (dataframe or csv)")
    merge_strategy: Optional[str] = Field(default=None, description="How to combine multiple datasets")

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

def process_query(query: str) -> Dict[str, pd.DataFrame]:
    """Process an F1 query and return processed DataFrames"""
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
        3. /circuits - Circuit data
        4. /qualifying - Qualifying performance
        5. /laps - Lap time data
        6. /pitstops - Pit stop data
        7. /finishingStatus - Finishing status data
        
        Remember:
        - Only select endpoints that directly provide needed data
        - Format: http://ergast.com/api/f1/{{year}}/[endpoint].json
        - Add parameters only if needed (e.g., driver, round)
        """)
        
        # Create processing request
        processing_request = EndpointProcessingRequest(
            endpoints=result_response.content.endpoints,
            output_format="dataframe",
            merge_strategy="auto"
        )
        
        # Process endpoints through transformers
        result_dfs = process_endpoints(processing_request)
        
        print(f"\nGenerated {len(result_dfs)} datasets:")
        for key, df in result_dfs.items():
            print(f"- {key}: {df.shape} rows")
        
        return result_dfs
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return {}

def test_queries(indices: List[int]):
    """Test the F1 query processor with query indices"""
    queries = query_index.get_queries(indices)
    for query in queries:
        process_query(query)

def route_endpoint_to_transformer(url: str) -> tuple:
    """Map API endpoints to transformer functions and parameters"""
    endpoint_map = {
        'results': ('transform_results', 'process_results_data'),
        'driverStandings': ('transform_standings', 'fetch_and_process_standings'),
        'constructorStandings': ('transform_standings', 'fetch_and_process_standings'),
        'laps': ('transform_status', 'fetch_and_process_lap_timings'),
        'qualifying': ('transform_qualifying', 'process_qualifying_data'),
        'pitstops': ('transform_pitstops', 'process_pitstop_data'),
        'finishingStatus': ('transform_status', 'process_finishing_status')
    }
    
    # Extract endpoint type from URL
    endpoint_type = next(
        (et for et in endpoint_map if f'/{et}' in url),
        'unknown'
    )
    
    # Extract parameters from URL
    parts = url.replace('.json', '').split('/')
    year = parts[-3] if parts[-3].isdigit() else None
    round_num = parts[-2] if parts[-2].isdigit() else None
    lap_number = parts[-1] if endpoint_type == 'laps' and parts[-1].isdigit() else None
    
    return endpoint_map.get(endpoint_type, (None, None)), {
        'year': int(year) if year else None,
        'round_num': int(round_num) if round_num else None,
        'lap_number': int(lap_number) if lap_number else None
    }

def process_endpoints(request: EndpointProcessingRequest) -> Dict[str, pd.DataFrame]:
    """Process endpoints through appropriate transformers"""
    dfs = {}
    
    for url in request.endpoints:
        # Route endpoint to transformer
        (module_name, func_name), params = route_endpoint_to_transformer(url)
        if not module_name or not func_name:
            print(f"No transformer found for {url}")
            continue
            
        try:
            # Import transformer module
            module = __import__(f"backend.qhi2.{module_name}", fromlist=[func_name])
            transformer_func = getattr(module, func_name)
            
            # Call transformer with parameters
            if module_name == 'transform_standings':
                df = transformer_func(params['standing_type'])
            else:
                df = transformer_func(
                    year=params['year'],
                    round_num=params['round_num'],
                    lap_number=params.get('lap_number')
                )
                
            # Store result
            key = f"{module_name}_{uuid.uuid4().hex[:6]}"
            dfs[key] = df
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
    
    return dfs

if __name__ == "__main__":
    test_queries([30]) 