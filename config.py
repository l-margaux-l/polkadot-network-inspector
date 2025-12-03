import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.resolve()
LOGS_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"
DB_DIR = PROJECT_ROOT / "db"

LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

# Polkadot RPC configuration
POLKADOT_RPC_URL = os.getenv("POLKADOT_RPC_URL", "wss://rpc.polkadot.io")
RPC_TIMEOUT = 10
RPC_MAX_RETRIES = 3

# Monitoring settings
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
ALERT_THRESHOLD_BLOCK_LAG = int(os.getenv("ALERT_THRESHOLD_BLOCK_LAG", "10"))
ALERT_THRESHOLD_PEERS = int(os.getenv("ALERT_THRESHOLD_PEERS", "1"))
ALERT_THRESHOLD_RPC_RESPONSE_TIME = 5.0

# Email notifications
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
ALERT_EMAIL_RECIPIENTS = os.getenv("ALERT_EMAIL_RECIPIENTS", "").split(",")

# Slack notifications
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
METRICS_LOG_FILE = LOGS_DIR / "metrics.log"
ALERTS_LOG_FILE = LOGS_DIR / "alerts.log"
MAIN_LOG_FILE = LOGS_DIR / "inspector.log"

# Database
DATABASE_URL = f"sqlite:///{DB_DIR / 'inspector.db'}"

# CSV export
CSV_EXPORT_DIR = DATA_DIR / "exports"
CSV_EXPORT_DIR.mkdir(exist_ok=True)

# Application metadata
APP_NAME = "Polkadot Network Inspector"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Monitor health and performance of Polkadot network nodes"
AUTHOR = "Marharyta Tretiak"
AUTHOR_EMAIL = "margotech.work@gmail.com"

# Debug mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Nodes configuration
NODES_CONFIG = [
    {
        "name": "Polkadot",
        "rpc_url": os.getenv("POLKADOT_RPC_URL", "wss://rpc.polkadot.io")
    },
    {
        "name": "Kusama",
        "rpc_url": "wss://kusama-rpc.polkadot.io"
    }
]
