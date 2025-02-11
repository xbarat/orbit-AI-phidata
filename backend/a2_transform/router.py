from .transformers import (
    RaceResultsTransformer,
    StandingsTransformer,
    QualifyingTransformer,
    StatusTransformer
)
from .transformers.laps import LapTimesTransformer
from .transformers.races import RaceScheduleTransformer
from .transformers.base import BaseTransformer
from typing import Optional

class EndpointRouter:
    def __init__(self):
        self.transformers = {
            'results': RaceResultsTransformer(),
            'standings': StandingsTransformer(),
            'qualifying': QualifyingTransformer(),
            'status': StatusTransformer(),
            'laps': LapTimesTransformer(),
            'races': RaceScheduleTransformer()
        }
    
    def get_transformer(self, endpoint: str) -> Optional[BaseTransformer]:
        """Get the appropriate transformer for an endpoint"""
        if '/results' in endpoint:
            return self.transformers['results']
        elif '/driverStandings' in endpoint or '/constructorStandings' in endpoint:
            return self.transformers['standings']
        elif '/qualifying' in endpoint:
            return self.transformers['qualifying']
        elif '/races' in endpoint:
            return self.transformers['races']
        elif '/laps/' in endpoint or '/status' in endpoint:
            return self.transformers['status']
        elif 'laps' in endpoint:
            return self.transformers['laps']
        return None 