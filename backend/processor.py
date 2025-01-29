import logging
from typing import List
from a1_query.query_to_endpoint import process_query
from a2_transform import EndpointRouter
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class F1QueryProcessor:
    """Minimal pipeline coordinator"""
    
    def __init__(self):
        self.router = EndpointRouter()
    
    def execute_query(self, query: str) -> List[str]:
        """Core execution flow"""
        try:
            # Step 1: Get endpoints using the existing process_query function
            endpoints = process_query(query)
            if not endpoints:
                logger.warning("No endpoints generated for query: %s", query)
                return []
            
            # Step 2: Process each endpoint through the router
            results = []
            for endpoint in endpoints:
                logger.info("Processing endpoint: %s", endpoint)
                transformer = self.router.get_transformer(endpoint)
                if transformer:
                    result = transformer.transform(endpoint)
                    results.append(result)
                else:
                    logger.warning("No transformer found for endpoint: %s", endpoint)
            
            return results
            
        except Exception as e:
            logger.error("Processing failed: %s", str(e))
            return []

# Test the minimal version
if __name__ == "__main__":
    processor = F1QueryProcessor()
    test_query = "Show me Verstappen's 2023 race results and qualifying performances"
    print("Testing query:", test_query)
    results = processor.execute_query(test_query)
    print("\nResults:")
    for idx, result in enumerate(results, 1):
        print(f"Result {idx}: {result}") 