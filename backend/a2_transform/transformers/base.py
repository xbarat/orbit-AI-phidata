class BaseTransformer:
    def transform(self, endpoint: str) -> str:
        return f"Processed {endpoint}"

class DriverStandingsTransformer(BaseTransformer):
    def transform(self, endpoint: str) -> str:
        return f"Driver standings data from {endpoint}"

class RaceResultsTransformer(BaseTransformer):
    def transform(self, endpoint: str) -> str:
        return f"Race results data from {endpoint}" 