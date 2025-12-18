#!/bin/bash

clear
echo "AVVIO DEMO OPENSTACK FORECASTING PLUGIN"
echo "=========================================="

# 1. PULIZIA TOTALE PRIMA DI PARTIRE
echo ""
echo "PULIZIA PROCESSI PRECEDENTI..."
pkill -f "python.*forecast" 2>/dev/null
pkill -f "python.*api" 2>/dev/null
rm -rf __pycache__ forecasting_plugin/__pycache__ 2>/dev/null
sleep 2

# 2. Mostra struttura
echo ""
echo "STRUTTURA DEL PROGETTO:"
find . -name "*.py" -o -name "*.sh" | grep -v venv | grep -v __pycache__ | sort

# 3. Attiva venv
echo ""
echo "ATTIVAZIONE AMBIENTE VIRTUALE..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtualenv attivato"
else
    echo "Virtualenv non trovato!"
    exit 1
fi


# 5. Avvia servizio CON VARIABILI AMBIENTE CHE DISABILITANO DEBUG
echo ""
echo "AVVIO SERVIZIO FORECASTING..."
echo "=========================================="
echo "Connessione: OpenStack"
echo "API: http://localhost:5000"
echo "Intervallo raccolta: 60 secondi"
echo ""
echo "ENDPOINT DISPONIBILI:"
echo "  • /api/v1/health"
echo "  • /api/v1/forecast/cpu?hours=12"
echo "  • /api/v1/forecast/ram?hours=12"
echo "  • /api/v1/alerts"
echo "  • /api/v1/metrics/current"
echo "=========================================="
echo ""
echo "LOG DEL SERVIZIO (CTRL+C per fermare):"
echo "══════════════════════════════════════════"

# 6. AVVIA CON VARIABILI AMBIENTE CHE FORZANO PRODUCTION
FLASK_ENV=production \
FLASK_DEBUG=0 \
PYTHONDONTWRITEBYTECODE=1 \
python -B -c "
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, '.')

# Importa e avvia
from forecasting_plugin.api import app

print('=' * 60)
print('SERVIZIO AVVIATO IN MODALITÀ PRODUZIONE')
print('=' * 60)

# Configurazione che BLOCCA OGNI DEBUG/RELOAD
app.run(
    host='0.0.0.0',
    port=5000,
    debug=False,
    use_reloader=False,
    threaded=True
)
"