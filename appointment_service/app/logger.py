import json
from datetime import datetime
import threading

def log_event(level: str, message: str, service="appointment-service", extra_data=None):
    """
    Structured JSON logging to STDOUT.
    Fluent Bit will collect and forward to OpenSearch.
    """

    def _log():
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "service": service,
            "message": message,
            "data": extra_data or {}
        }

        # Print JSON → Kubernetes → Fluent Bit → OpenSearch
        print(json.dumps(log_record))

    # Non-blocking logging
    threading.Thread(target=_log).start()
