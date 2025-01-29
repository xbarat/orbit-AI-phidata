import logging
from typing import List
from a1_query.query_to_endpoint import process_query
from a2_transform import EndpointRouter

class F1QueryProcessor:
    """Minimal pipeline coordinator"""
    
    def __init__(self):
        self.router = EndpointRouter()
    
    def execute_query(self, query: str) -> List[str]:
        """Core execution flow"""
        try:
            # Step 1: Get endpoints
            endpoints = process_query(query)
            if not endpoints:
                return []
            
            # Step 2: Process endpoints
            results = []
            for endpoint in endpoints:
                if transformer := self.router.get_transformer(endpoint):
                    results.append(transformer.transform(endpoint))
            
            return results
            
        except Exception as e:
            logging.error(f"Processing failed: {str(e)}")
            return []

# Test the minimal version
if __name__ == "__main__":
    processor = F1QueryProcessor()
    test_query = "Show me Lewis Hamilton's 2023 race results"
    print("Testing query:", test_query)
    print("Results:", processor.execute_query(test_query)) 