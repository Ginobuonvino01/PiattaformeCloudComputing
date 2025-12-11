import os


class Config:
    # OpenStack credentials
    OS_AUTH_URL = os.getenv('OS_AUTH_URL', 'http://controller:5000/v3')
    OS_USERNAME = os.getenv('OS_USERNAME', 'admin')
    OS_PASSWORD = os.getenv('OS_PASSWORD', 'secret')
    OS_PROJECT_NAME = os.getenv('OS_PROJECT_NAME', 'admin')

    # Plugin settings
    COLLECTION_INTERVAL = 300  # secondi
    HISTORY_LENGTH = 1000
    FORECAST_HORIZON = 24  # ore

    # API settings
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG = True

    # Alert thresholds
    CPU_WARNING = 70
    CPU_CRITICAL = 85
    RAM_WARNING = 75
    RAM_CRITICAL = 90