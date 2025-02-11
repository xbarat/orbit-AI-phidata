import json
import matplotlib.pyplot as plt
from typing import Dict, List

class AnalysisAgent:
    def __init__(self, data: Dict):
        self.raw_data = data
        self.dfs = self._load_dataframes()
        
    def _load_dataframes(self) -> List[pd.DataFrame]:
        """Convert raw data to DataFrames"""
        return [pd.DataFrame(records) for records in self.raw_data['results']['data']]
    
    def analyze(self, query: str) -> Dict:
        """Generate analysis using LLM"""
        prompt = self._build_prompt(query)
        response = self._call_llm(prompt)
        return self._parse_response(response)
    
    def visualize(self, instruction: str) -> str:
        """Generate visualization based on LLM instructions"""
        try:
            # Secure code execution
            allowed_imports = {'plt': matplotlib.pyplot, 'pd': pd}
            exec(instruction, {"__builtins__": None}, allowed_imports)
            plt.savefig('output.png')
            return 'output.png'
        except Exception as e:
            return f"Visualization error: {str(e)}"
    
    def _build_prompt(self, query: str) -> str:
        """Construct LLM prompt with data context"""
        data_sample = json.dumps(
            {col: list(df[col].head(3)) for df in self.dfs for col in df.columns},
            indent=2
        )
        
        return f"""
        Analyze this Formula 1 data to answer: {query}
        Data sample:
        {data_sample}
        
        Provide your response in JSON format with:
        - "insights": list of key findings
        - "recommendations": list of suggestions
        - "visualization_code": Python code using matplotlib
        """
    
    def _call_llm(self, prompt: str) -> Dict:
        """Mock LLM call - integrate with actual API"""
        # Replace with actual LLM API call
        return {
            "insights": ["Sample insight 1", "Sample insight 2"],
            "recommendations": ["Sample recommendation"],
            "visualization_code": "plt.plot([1,2,3])"
        }
    
    def _parse_response(self, response: Dict) -> Dict:
        """Parse and validate LLM response"""
        return {
            "insights": response.get('insights', []),
            "recommendations": response.get('recommendations', []),
            "visualization_code": response.get('visualization_code', '')
        } 