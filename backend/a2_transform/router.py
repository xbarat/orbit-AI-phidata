from .transformers import (
    RaceResultsTransformer,
    StandingsTransformer,
    QualifyingTransformer,
    StatusTransformer
)

class EndpointRouter:
    def __init__(self):
        self.transformers = {
            'results': RaceResultsTransformer(),
            'standings': StandingsTransformer(),
            'qualifying': QualifyingTransformer(),
            'status': StatusTransformer()
        }
    
    def get_transformer(self, endpoint: str):
        """Match endpoint patterns to transformers"""
        if '/results' in endpoint:
            return self.transformers['results']
        elif '/driverStandings' in endpoint or '/constructorStandings' in endpoint:
            return self.transformers['standings']
        elif '/qualifying' in endpoint:
            return self.transformers['qualifying']
        elif '/laps/' in endpoint or '/status' in endpoint:
            return self.transformers['status']
        return None 