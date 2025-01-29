from phi.agent import Agent
from phi.openai import OpenAI

from typing import Dict, List
from pydantic import BaseModel

class DataRequirement(BaseModel):
    endpoint: str
    params: Dict[str, str]

class QueryProcessor:
    def __init__(self):
        self.agent = Agent(
            name="Query Processor",
            instructions=[
                "Analyze F1 queries to identify required endpoints and parameters",
                "Break down complex queries into endpoint requirements",
                "Map driver names and statistics to appropriate API endpoints"
            ]
        )
    
    def process_query(self, query: str) -> List[DataRequirement]:
        """
        Process a user query and return the data requirements.
        
        Args:
            query: The user's natural language query about F1 statistics
            
        Returns:
            List of DataRequirement objects specifying needed endpoints and parameters
        """
        # The agent will analyze the query and return structured requirements
        requirements = self.agent.execute({
            "task": "analyze_query",
            "query": query
        })
        
        # Convert the agent's output to DataRequirement objects
        return [DataRequirement(**req) for req in requirements] 