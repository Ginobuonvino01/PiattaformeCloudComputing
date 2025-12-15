import os

class Config:
    # Credenziali OpenStack
    OS_AUTH_URL = os.getenv('OS_AUTH_URL', 'http://localhost/identity/v3')
    OS_USERNAME = os.getenv('OS_USERNAME', 'admin')
    OS_PASSWORD = os.getenv('OS_PASSWORD', 'secret')
    OS_PROJECT_NAME = os.getenv('OS_PROJECT_NAME', 'admin')

    # Impostazioni Plugin
    COLLECTION_INTERVAL = 60  # 1 minuto
    HISTORY_LENGTH = 1000
    FORECAST_HORIZON = 24

    # Impostazioni API
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG = True

    # Alert Soglie
    CPU_WARNING = 25  # 25% - Facile da raggiungere
    CPU_CRITICAL = 40  # 40%
    RAM_WARNING = 30  # 30%
    RAM_CRITICAL = 50  # 50%
    STORAGE_WARNING = 70  # 70%