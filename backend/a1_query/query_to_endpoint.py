from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field
from phi.agent import Agent
from phi.model.openai import OpenAIChat
import os
from dotenv import load_dotenv
from .query_index import query_index
from .url_builder import ErgastURLBuilder
from .models import (
    QueryParameters,
    EndpointInfo,
    F1QueryResponse,
    QueryType
)

# Load environment variables
load_dotenv()

# Get API key from environment variable
openai = OpenAIChat(api_key=os.getenv('OPENAI_API_KEY'))

class EntityInfo(BaseModel):
    """Information about entities in the query"""
    drivers: List[str] = Field(default_factory=list, description="List of driver IDs (e.g., lewis_hamilton)")
    constructors: List[str] = Field(default_factory=list, description="List of constructor IDs (e.g., mercedes)")
    circuits: List[str] = Field(default_factory=list, description="List of circuit IDs (e.g., monza)")
    years: List[str] = Field(default_factory=list, description="List of years to query")
    rounds: List[str] = Field(default_factory=list, description="List of specific rounds if needed")

class MetricRequirement(BaseModel):
    """Specific metrics needed from the data"""
    race_results: bool = Field(default=False, description="Need race results data")
    qualifying: bool = Field(default=False, description="Need qualifying data")
    lap_times: bool = Field(default=False, description="Need lap timing data")
    pit_stops: bool = Field(default=False, description="Need pit stop data")
    standings: bool = Field(default=False, description="Need standings data")
    status: bool = Field(default=False, description="Need race status/finishing data")

def create_understanding_agent():
    """Create an agent focused solely on extracting structured parameters"""
    return Agent(
        model=openai,
        description="Expert Formula 1 query analyzer that extracts entities and metrics",
        output_model=QueryParameters,
        instructions=[
            "Query Analysis Protocol:",
            "1. Entity Identification:",
            "   - Drivers: Convert to lowercase IDs (Fernando Alonso → fernando_alonso)",
            "   - Circuits: Use official circuit IDs (Silverstone → silverstone)",
            "   - Constructors: Official team IDs (Aston Martin → aston_martin)",
            "",
            "2. Temporal Analysis:",
            "   - Explicit years: Set time_scope.years=[2018, 2019, 2020]",
            "   - Year range: Set time_scope.range=[2018, 2020]",
            "   - Relative: Set time_scope.last=5 for 'last 5 seasons'",
            "   - Default: time_scope.years=[current_year] if not specified",
            "",
            "3. Metric Detection:",
            "   - Race results → metrics=['results']",
            "   - Qualifying → metrics=['qualifying']",
            "   - Standings → metrics=['standings']",
            "   - Status/DNF → metrics=['status']",
            "",
            "4. Output Format:",
            "   primary_entity: 'driver' | 'constructor' | 'circuit' | 'season'",
            "   entity_ids: {",
            "     'drivers': ['alonso', 'hamilton'],",
            "     'circuits': ['silverstone'],",
            "     'constructors': []",
            "   }",
            "   metrics: ['results', 'qualifying', etc]",
            "   time_scope: {",
            "     'years': [2020, 2021, 2022] or",
            "     'range': [2020, 2022] or",
            "     'last': 5",
            "   }",
            "   comparison: true/false",
            "Time Scope Handling:",
            "- 'in a given season' → time_scope.years=[current_year]",
            "- 'this season' → time_scope.years=[current_year]",
            "- 'last season' → time_scope.years=[current_year-1]",
            
            "Metric Mapping:",
            "- 'qualifying position' → metrics=['qualifying']",
            "- 'grid position' → metrics=['qualifying']",
            "- 'pole positions' → metrics=['qualifying']",
            
            "Driver ID Formatting:",
            "- First and last name: 'oscar_piastri'",
            "- Last name only: Append first name if known",
            "Qualifying Query Examples:",
            "1. 'average qualifying position':",
            "   primary_entity: 'driver'",
            "   entity_ids: {'drivers': ['oscar_piastri']}",
            "   metrics: ['qualifying']",
            "   time_scope: {'years': [2024]}",
            "",
            "2. 'qualifying performance':",
            "   metrics: ['qualifying']",
            "   Add 'qualifying' to metrics for any grid/position/pole related queries",
            "",
            "3. Default Behaviors:",
            "   - 'in a given season' → Use current year",
            "   - 'qualifying' → Always include in metrics",
            "   - Driver names → Convert to lowercase with underscore",
        ]
    )

def create_endpoint_agent():
    """Create an agent that maps parameters to Ergast API endpoints"""
    return Agent(
        model=openai,
        description="You are a Formula 1 data engineer who determines the optimal endpoint strategy",
        output_model=F1QueryResponse,
        instructions=[
            "Endpoint Construction Rules:",
            "1. Base Patterns:",
            "   - Driver-focused: /f1/{year}/drivers/{driverId}/results.json",
            "   - Circuit-focused: /f1/circuits/{circuitId}/{year}/results.json",
            "   - Constructor-focused: /f1/constructors/{constructorId}/{year}/results.json",
            "   - Comparison: Multiple driver/constructor endpoints",
            "",
            "2. Temporal Handling:",
            "   - For multi-year requests: One endpoint per year",
            "   - Season ranges: 2018-2023 → separate yearly endpoints",
            "",
            "3. Data Composition:",
            "   - Pit stops require /lapTimes endpoints",
            "   - Standings need /driverStandings and /constructorStandings",
            "",
            "4. Filtering Guidance:",
            "Example: For 'Alonso at Silverstone':",
            "1. First get all Silverstone races: /f1/circuits/silverstone/races.json",
            "2. For each race year: /f1/{year}/circuits/silverstone/results.json?driver=alonso",
            "3. Add status endpoint for each race: /f1/{year}/{round}/status.json"
        ]
    )

def process_query(query: str) -> List[str]:
    """Process an F1 query and return relevant Ergast API endpoint URLs"""
    try:
        # Step 1: Extract structured parameters using the understanding agent
        understanding_agent = create_understanding_agent()
        params_response = understanding_agent.run(f"""
        Analyze this Formula 1 query:
        "{query}"

        Follow the systematic analysis framework to determine exact data requirements.
        Ensure all identifiers are properly formatted (lowercase with underscores).
        Consider any implicit requirements that might need filtering or post-processing.
        """)
        
        # Debug logging
        print("\nExtracted Parameters:")
        print(f"Primary Entity: {params_response.content.primary_entity}")
        print(f"Entity IDs: {params_response.content.entity_ids}")
        print(f"Metrics: {params_response.content.metrics}")
        print(f"Time Scope: {params_response.content.time_scope}")
        print(f"Comparison: {params_response.content.comparison}")
        
        # New rule-based URL construction
        url_builder = ErgastURLBuilder()
        endpoints = url_builder.build_endpoints(params_response.content)
        
        # Output results
        print(f"\nQuery: {query}")
        print("Required Endpoints:")
        for endpoint in endpoints:
            print(f"- {endpoint}")
        
        return endpoints
        
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