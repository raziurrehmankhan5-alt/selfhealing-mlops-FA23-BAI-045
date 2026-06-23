import requests
import time
from prometheus_client import start_http_server, Gauge

# Define the metric
prediction_confidence_score = Gauge(
    'prediction_confidence_score',
    'Latest prediction confidence score from ML API'
)

# Configuration
APP_URL = "http://localhost:32500/api/latest-confidence"
EXPORTER_PORT = 8000
POLL_INTERVAL = 5

def poll_confidence():
    """Poll the app's confidence endpoint and update the metric."""
    while True:
        try:
            response = requests.get(APP_URL, timeout=3)
            data = response.json()
            confidence = data.get('confidence', 1.0)
            prediction_confidence_score.set(confidence)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Confidence: {confidence:.4f}")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error polling {APP_URL}: {e}")
            prediction_confidence_score.set(1.0)
        
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    print(f"Starting Prometheus exporter on port {EXPORTER_PORT}...")
    start_http_server(EXPORTER_PORT)
    print(f"Exporter listening on http://localhost:{EXPORTER_PORT}/metrics")
    print(f"Polling {APP_URL} every {POLL_INTERVAL} seconds...")
    
    try:
        poll_confidence()
    except KeyboardInterrupt:
        print("\nExporter stopped.")
