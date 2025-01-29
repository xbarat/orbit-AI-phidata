import re

class ErgastEndpointValidator:
    ENDPOINT_PATTERNS = {
        'results': r"^/f1/(\d{4}/)?(drivers|constructors|circuits)/[a-z_]+/results\.json$",
        'qualifying': r"^/f1/(\d{4}/)?((drivers/[a-z_]+/)|(circuits/[a-z_]+/))?qualifying\.json(\?driver=[a-z_]+)?$",
        'standings': r"^/f1/(\d{4}/)?(driver|constructor)Standings\.json$",
        'status': r"^/f1/(\d{4}/)?(\d+/)?status\.json$",
        'laps': r"^/f1/(\d{4}/)?(\d+/)?laps(/\d+)?\.json$",
        'circuit_list': r"^/f1/circuits\.json$"
    }

    def validate(self, endpoint: str) -> bool:
        """Validate against all known endpoint patterns"""
        path = endpoint.replace("http://ergast.com/api", "")
        return any(
            re.match(pattern, path)
            for pattern in self.ENDPOINT_PATTERNS.values()
        ) 