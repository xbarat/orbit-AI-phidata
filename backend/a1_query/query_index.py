from typing import Dict, List, Optional
import os
import json
from pathlib import Path

# Update the path to point to workspace root eval directory
INDEX_DIR = Path(__file__).parent.parent.parent / "eval"
INDEX_DIR.mkdir(exist_ok=True, parents=True)
INDEX_FILE = INDEX_DIR / "query_index.json"

class QueryIndex:
    def __init__(self):
        self.queries: Dict[int, Dict] = {}
        self.query_files = [
            'query-history.txt',
            'query-history-advanced.txt',
            'query-focus-basic.txt',
            'query-focus-advanced.txt',
            'query-edge.txt',
            'query-ambiguous.txt',
            'query-comparison.txt',
            'query-stats.txt'
        ]
        self._load_queries()
        
    def _extract_queries_from_file(self, content: str, source_file: str) -> List[Dict]:
        """Extract queries from file content and return with metadata"""
        queries = []
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('"'):
                continue
                
            query_text = None
            if line.startswith('- '):
                query_text = line[2:]
            elif line[0].isdigit() and '. ' in line:
                query_text = line.split('. ', 1)[1]
                
            if query_text:
                queries.append({
                    'query': query_text,
                    'source': source_file,
                    'category': source_file.replace('.txt', '').replace('query-', '')
                })
        return queries

    def _load_queries(self):
        """Load queries from the JSON index file"""
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r') as f:
                self.queries = json.load(f)
        else:
            print(f"Warning: Query index file not found at {INDEX_FILE}")
            self.queries = {"total_queries": 0, "queries": {}}
        
    def _save_index(self):
        """Save the current index to a JSON file for reference"""
        INDEX_DIR.mkdir(exist_ok=True, parents=True)
        with open(INDEX_FILE, 'w') as f:
            json.dump(self.queries, f, indent=2)
    
    def get_query(self, index: int) -> Optional[str]:
        """Get query text by index number"""
        if str(index) in self.queries.get('queries', {}):
            return self.queries['queries'][str(index)]['query']
        return None
    
    def get_query_info(self, index: int) -> Optional[Dict]:
        """Get full query information by index number"""
        return self.queries.get('queries', {}).get(str(index))
    
    def get_queries(self, indices: List[int]) -> List[str]:
        """Get multiple queries by their indices"""
        return [self.get_query(i) for i in indices if self.get_query(i) is not None]
    
    def get_category_indices(self, category: str) -> List[int]:
        """Get all query indices for a specific category"""
        return [
            idx for idx, data in self.queries.items() 
            if data['category'] == category
        ]
    
    def total_queries(self) -> int:
        """Get total number of indexed queries"""
        return len(self.queries)
        
    def display_index(self, category: Optional[str] = None):
        """Display queries with their indices in a readable format
        
        Args:
            category: Optional category to filter queries
        """
        queries = self.queries
        if category:
            queries = {
                idx: data for idx, data in queries.items()
                if data['category'] == category
            }
            
        print(f"\nQuery Index {'for ' + category if category else ''}")
        print("=" * 50)
        
        for idx, data in sorted(queries.items()):
            print(f"\n[{idx}] {data['query']}")
            print(f"    Category: {data['category']}")
            print(f"    Source: {data['source']}")
        
        print(f"\nTotal queries: {len(queries)}")

# Create singleton instance
query_index = QueryIndex()

# Mock query for testing
query_index.get_queries([0]) 