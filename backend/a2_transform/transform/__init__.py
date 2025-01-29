from urllib.parse import urlparse
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EndpointRouter:
    """Routes Ergast API endpoints to appropriate transformers"""
    
    def __init__(self):
        self.endpoint_map = {
            r'/results(\.json)?$': 'results',
            r'/driverStandings(\.json)?$': 'standings',
            r'/laps/\d+(\.json)?$': 'status',
            r'/qualifying(\.json)?$': 'qualifying'
        }
        
        # Lazy load transformers to avoid circular imports
        self._transformers = {}
    
    def _load_transformer(self, name: str):
        """Lazy load transformer modules"""
        if name not in self._transformers:
            try:
                if name == 'results':
                    from .transform_results import ResultsTransformer
                    self._transformers[name] = ResultsTransformer()
                elif name == 'standings':
                    from .transform_standings import StandingsTransformer
                    self._transformers[name] = StandingsTransformer()
                elif name == 'status':
                    from .transform_status import StatusTransformer
                    self._transformers[name] = StatusTransformer()
                elif name == 'qualifying':
                    from .transform_qualifying import QualifyingTransformer
                    self._transformers[name] = QualifyingTransformer()
            except ImportError as e:
                logger.error(f"Failed to load transformer {name}: {str(e)}")
                return None
        return self._transformers.get(name)
    
    def get_transformer(self, endpoint: str):
        """Match endpoint to transformer module"""
        path = urlparse(endpoint).path
        
        for pattern, module_name in self.endpoint_map.items():
            if re.search(pattern, path):
                transformer = self._load_transformer(module_name)
                if transformer:
                    return transformer
                
        logger.warning(f"No transformer found for endpoint: {endpoint}")
        return None 