from phi.agent import Agent
import pandas as pd
from typing import Dict, Any

class AnalysisAgent:
    def __init__(self):
        self.agent = Agent(
            name="Analysis Agent",
            instructions=[
                "Analyze F1 statistics and generate insights",
                "Compare driver and team performances",
                "Generate statistical summaries and trends"
            ]
        )
    
    def analyze_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the transformed data and generate insights.
        
        Args:
            data: Pandas DataFrame containing the transformed F1 data
            
        Returns:
            Dictionary containing analysis results and insights
        """
        insights = self.agent.execute({
            "task": "analyze_data",
            "data": data.to_dict()
        })
        
        return insights 