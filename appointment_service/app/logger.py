import os
import threading
import json
from datetime import datetime
from opensearchpy import OpenSearch

# 1. Configuration (Load from Env Vars for "12-Factor App" best practices)
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch-service") # K8s Service Name
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", 9200))

# 2. Initialize Client
client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
    http_compress=True,
    use_ssl=False
)

def log_event(level: str, message: str, service="appointment-service", extra_data=None):
    """
    Sends a structured log to OpenSearch in the background.
    """
    def _send():
        try:
            # Structure the log for Grafana
            document = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': level.upper(),
                'service': service,
                'message': message,
                'data': extra_data or {}
            }
            
            # Send to Index 'salon-logs'
            client.index(
                index='salon-logs',
                body=document
            )
            print(f"[{level.upper()}] Log sent: {message}") # Local backup log
            
        except Exception as e:
            # Fallback: Print to console so Kubernetes logs still catch it
            print(f"!! LOGGING FAILED !! {str(e)}")

    # Run in background thread (Fire & Forget)
    threading.Thread(target=_send).start()