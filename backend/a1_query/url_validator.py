import re

class ErgastEndpointValidator:
    ENDPOINT_PATTERNS = {
        'season': r"^/f1/seasons$",
        'circuit': r"^/f1/circuits$",
        'race': r"^/f1/\d{4}(/races)?$",
        'constructor': r"^/f1/\d{4}/constructors$",
        'driver': r"^/f1/\d{4}/drivers$",
        'result': r"^/f1/\d{4}/(drivers|constructors|circuits)/[a-z_]+/results\.json$",
        'sprint': r"^/f1/\d{4}/sprint$",
        'qualifying': r"^/f1/\d{4}/qualifying$",
        'pitstop': r"^/f1/\d{4}/\d+/pitstops$",
        'lap': r"^/f1/\d{4}/\d+/laps\.json$",
        'driverstanding': r"^/f1/\d{4}/driverStandings\.json$",
        'constructorstanding': r"^/f1/\d{4}/(constructors/[a-z_]+/)?constructorStandings\.json$",
        'status': r"^/f1/\d{4}/(constructors/[a-z_]+/)?status\.json$"
    }

    def validate(self, endpoint: str) -> bool:
        """Validate against all known endpoint patterns"""
        path = endpoint.replace("http://ergast.com/api", "")
        return any(
            re.match(pattern, path)
            for pattern in self.ENDPOINT_PATTERNS.values()
        ) 