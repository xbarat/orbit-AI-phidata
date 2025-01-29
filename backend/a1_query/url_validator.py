import re

class ErgastEndpointValidator:
    # Driver ID mappings for Ergast API
    DRIVER_MAPPINGS = {
        'max_verstappen': 'max_verstappen',
        'hamilton': 'hamilton',
        'leclerc': 'leclerc',
        'perez': 'perez',
        'carlos_sainz': 'sainz',
        'carlos_sainz_jr': 'sainz',
        'sainz': 'sainz',
        'russell': 'russell',
        'norris': 'norris',
        'oscar_piastri': 'piastri',
        'piastri': 'piastri',
        'alonso': 'alonso',
        'stroll': 'stroll',
        'gasly': 'gasly',
        'ocon': 'ocon',
        'albon': 'albon',
        'tsunoda': 'tsunoda',
        'bottas': 'bottas',
        'hulkenberg': 'hulkenberg',
        'ricciardo': 'ricciardo',
        'zhou': 'zhou',
        'kevin_magnussen': 'kevin_magnussen',
        'sargeant': 'sargeant'
    }

    ENDPOINT_PATTERNS = {
        'season': r"^/f1/seasons$",
        'circuit': r"^/f1/circuits$",
        'race': r"^/f1/\d{4}(/races)?$",
        'constructor': r"^/f1/\d{4}/constructors$",
        'driver': r"^/f1/\d{4}/drivers$",
        'result': r"^/f1/\d{4}/(drivers|constructors|circuits)/[a-z_]+/results\.json$",
        'sprint': r"^/f1/\d{4}/sprint$",
        'qualifying': r"^/f1/\d{4}/drivers/[a-z_]+/qualifying\.json$",
        'pitstop': r"^/f1/\d{4}/\d+/pitstops$",
        'lap': r"^/f1/\d{4}/\d+/laps\.json$",
        'driverstanding': r"^/f1/\d{4}/driverStandings\.json$",
        'constructorstanding': r"^/f1/\d{4}/constructorStandings\.json$",
        'status': r"^/f1/\d{4}/(constructors/[a-z_]+/)?status\.json$"
    }

    def validate(self, endpoint: str) -> bool:
        """Validate against all known endpoint patterns"""
        path = endpoint.replace("http://ergast.com/api", "")
        
        # Debug print
        print(f"Validating path: {path}")
        
        # Map driver IDs if present
        for driver_id, ergast_id in self.DRIVER_MAPPINGS.items():
            if f"/drivers/{driver_id}/" in path:
                old_path = path
                path = path.replace(f"/drivers/{driver_id}/", f"/drivers/{ergast_id}/")
                if old_path != path:
                    print(f"Mapped path from {old_path} to {path}")
            elif f"/drivers/{driver_id}" in path:
                old_path = path
                path = path.replace(f"/drivers/{driver_id}", f"/drivers/{ergast_id}")
                if old_path != path:
                    print(f"Mapped path from {old_path} to {path}")
        
        # Debug print
        print(f"Final path to validate: {path}")
        
        return any(
            re.match(pattern, path)
            for pattern in self.ENDPOINT_PATTERNS.values()
        ) 