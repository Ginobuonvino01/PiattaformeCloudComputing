#!/usr/bin/env python3
"""
Script principale per avviare il servizio di forecasting
"""
import sys
import os
import logging

# Aggiungi la directory corrente al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from forecasting_plugin.api import app
    from forecasting_plugin.config import Config
    from forecasting_plugin.collector import MetricsCollector
    from forecasting_plugin.predictor import ResourcePredictor

    logger.info("Import dei moduli completato con successo")

except ImportError as e:
    logger.error(f"Errore nell'import dei moduli: {e}")
    logger.error("Assicurati che:")
    logger.error("1. La struttura delle cartelle sia corretta")
    logger.error("2. Tutti i moduli siano nella cartella forecasting_plugin/")
    logger.error("3. Le dipendenze siano installate (pip install -r requirements.txt)")
    sys.exit(1)


def init_forecasting_service():
    """Inizializza e avvia il servizio di forecasting"""
    try:
        # Log delle configurazioni (senza password)
        logger.info(f"Configurazione OpenStack:")
        logger.info(f"  Auth URL: {Config.OS_AUTH_URL}")
        logger.info(f"  Username: {Config.OS_USERNAME}")
        logger.info(f"  Project: {Config.OS_PROJECT_NAME}")

        # Inizializza collector
        collector = MetricsCollector(
            auth_url=Config.OS_AUTH_URL,
            username=Config.OS_USERNAME,
            password=Config.OS_PASSWORD,
            project_name=Config.OS_PROJECT_NAME
        )

        # Inizializza predictor
        predictor = ResourcePredictor()

        logger.info("Servizio di forecasting inizializzato con successo")
        logger.info(f"Endpoint disponibili:")
        logger.info(f"  GET /api/v1/health")
        logger.info(f"  GET /api/v1/forecast/cpu")
        logger.info(f"  GET /api/v1/forecast/ram")
        logger.info(f"  GET /api/v1/alerts")

        return collector, predictor

    except Exception as e:
        logger.error(f"Errore nell'inizializzazione del servizio: {e}")
        return None, None


def main():
    """Funzione principale"""
    logger.info("=" * 50)
    logger.info("Avvio OpenStack Forecasting Plugin")
    logger.info("=" * 50)

    # Inizializza il servizio
    collector, predictor = init_forecasting_service()

    if collector is None:
        logger.warning("Il servizio verrà avviato in modalità demo senza collector")

    # Avvia il server Flask
    try:
        logger.info(f"Avvio server Flask su {Config.API_HOST}:{Config.API_PORT}")
        logger.info(f"Debug mode: {Config.DEBUG}")

        app.run(
            host=Config.API_HOST,
            port=Config.API_PORT,
            debug=Config.DEBUG,
            use_reloader=False  # Disabilita reloader in produzione
        )

    except Exception as e:
        logger.error(f"Errore nell'avvio del server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()