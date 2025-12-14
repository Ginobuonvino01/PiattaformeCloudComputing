import os


class Config:
    # OpenStack credentials
    OS_AUTH_URL = os.getenv('OS_AUTH_URL', 'http://localhost/identity/v3')
    OS_USERNAME = os.getenv('OS_USERNAME', 'admin')
    OS_PASSWORD = os.getenv('OS_PASSWORD', 'secret')
    OS_PROJECT_NAME = os.getenv('OS_PROJECT_NAME', 'admin')

    # Plugin settings
    COLLECTION_INTERVAL = 60  # 1 minuto
    HISTORY_LENGTH = 1000
    FORECAST_HORIZON = 24

    # API settings
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG = True

    # Alert thresholds - PERFETTE PER DEMO!
    CPU_WARNING = 25  # 25% - Facile da raggiungere
    CPU_CRITICAL = 40  # 40%
    RAM_WARNING = 30  # 30%
    RAM_CRITICAL = 50  # 50%
    STORAGE_WARNING = 70  # 70%