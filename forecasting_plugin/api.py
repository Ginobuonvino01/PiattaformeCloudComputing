# Crea l'API REST con Flask. 5 endpoint per monitorare OpenStack.
import os
import sys

# ===== FORZA PRODUCTION MODE =====
# Disabilita COMPLETAMENTE il debug/reload di Flask
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'
sys.dont_write_bytecode = True  # No .pyc files
# =================================

from flask import Flask, jsonify, request
from datetime import datetime
from .collector import collector
from .predictor import ResourcePredictor

app = Flask(__name__)

# Variabile globale per tracciare se il collector è già stato avviato
_COLLECTOR_STARTED = False

# Avvia il collector SOLO se non è già in esecuzione
if not _COLLECTOR_STARTED:
    if not collector.running:
        collector.start_collection()
        _COLLECTOR_STARTED = True
        print(f"🚀 Collector avviato dal modulo API")
    else:
        print(f"ℹ️  Collector già in esecuzione (non riavviato)")


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    current = collector.get_current_metrics()  # Chiede metriche al collector

    return jsonify({
        'status': 'healthy',
        'service': 'openstack-forecasting-plugin',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'openstack_connected': collector.conn is not None,  # True se connesso
        'metrics': {
            'cpu': current['cpu']['value'] if 'cpu' in current else 0,
            'ram': current['ram']['value'] if 'ram' in current else 0,
        }
    })


@app.route('/api/v1/forecast/cpu', methods=['GET'])
def forecast_cpu():
    try:
        hours = request.args.get('hours', default=24, type=int)
        history = collector.get_metrics_history()
        values = [m['value'] for m in history['cpu'][-168:]]  # Ultime 168 ore

        predictor = ResourcePredictor()  # Crea un'istanza del predictor
        forecast = predictor.sinusoidal_with_trend(values, hours)

        return jsonify({
            'metric': 'cpu_usage_percent',
            'forecast_hours': hours,
            'predictions': forecast,
            'current_value': values[-1] if values else 0,
            'data_source': 'OpenStack' if collector.conn else 'Mock',
            'model': 'sinusoidal_with_trend',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/forecast/ram', methods=['GET'])
def forecast_ram():
    try:
        hours = request.args.get('hours', default=24, type=int)
        history = collector.get_metrics_history()
        values = [m['value'] for m in history['ram'][-168:]]

        predictor = ResourcePredictor()
        forecast = predictor.sinusoidal_with_trend(values, hours)

        return jsonify({
            'metric': 'ram_usage_percent',
            'forecast_hours': hours,
            'predictions': forecast,
            'current_value': values[-1] if values else 0,
            'data_source': 'OpenStack' if collector.conn else 'Mock',
            'model': 'sinusoidal_with_trend',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/alerts', methods=['GET'])
def get_alerts():
    alerts = []
    current = collector.get_current_metrics()

    # Alert CPU > 80%
    if 'cpu' in current:
        cpu_val = current['cpu']['value']
        if cpu_val > 80:
            alerts.append({
                'severity': 'WARNING',
                'resource': 'CPU',
                'message': f'High CPU usage: {cpu_val:.1f}%',
                'value': cpu_val
            })

    # Alert RAM >75%
    if 'ram' in current:
        ram_val = current['ram']['value']
        if ram_val > 75:
            alerts.append({
                'severity': 'WARNING',
                'resource': 'RAM',
                'message': f'High RAM usage: {ram_val:.1f}%',
                'value': ram_val
            })

    return jsonify({
        'alerts': alerts,
        'count': len(alerts),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/v1/openstack/info', methods=['GET'])
def openstack_info():
    info = collector.get_openstack_info()  # Chiede info dettagliate
    info['timestamp'] = datetime.now().isoformat()
    return jsonify(info)


@app.route('/api/v1/debug/collect-now', methods=['POST'])
def debug_collect_now():
    """Forza una raccolta immediata delle metriche (debug)"""
    success = collector.collect_once()
    current = collector.get_current_metrics()

    return jsonify({
        'success': success,
        'timestamp': datetime.now().isoformat(),
        'metrics': {
            'cpu': current['cpu']['value'] if 'cpu' in current else 0,
            'ram': current['ram']['value'] if 'ram' in current else 0,
            'storage': current['storage']['value'] if 'storage' in current else 0,
            'source_cpu': current['cpu']['source'] if 'cpu' in current else 'none',
            'source_ram': current['ram']['source'] if 'ram' in current else 'none',
            'source_storage': current['storage']['source'] if 'storage' in current else 'none'
        }
    })


@app.route('/api/v1/metrics/current', methods=['GET'])
def get_current_metrics():
    current = collector.get_current_metrics()
    return jsonify({
        'cpu_percent': current['cpu']['value'],
        'ram_percent': current['ram']['value'],
        'data_source': current['cpu']['source'],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/v1/metrics/history', methods=['GET'])
def get_metrics_history():
    limit = request.args.get('limit', default=100, type=int)
    history = collector.get_metrics_history()

    return jsonify({
        'cpu': history['cpu'][-limit:],
        'ram': history['ram'][-limit:],
        'timestamp': datetime.now().isoformat()
    })


# ===== FUNZIONE PER AVVIARE L'APP =====
def run_app():
    """Funzione per avviare l'applicazione Flask"""
    print("\n" + "=" * 60)
    print("🚀 OPENSTACK AI FORECASTING SERVICE")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 Data source: {'✅ OpenStack' if collector.conn else '🤖 Mock data'}")
    print(f"🔗 API: http://0.0.0.0:5000")
    print(f"⏱️  Collector interval: {collector.interval}s")
    print("=" * 60)
    print("🌐 Endpoints disponibili:")
    print("  • GET  /api/v1/health")
    print("  • GET  /api/v1/forecast/cpu?hours=24")
    print("  • GET  /api/v1/forecast/ram?hours=24")
    print("  • GET  /api/v1/alerts")
    print("  • GET  /api/v1/metrics/current")
    print("  • GET  /api/v1/openstack/info")
    print("=" * 60 + "\n")

    # Avvia Flask SENZA DEBUG e SENZA RELOADER
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # ASSOLUTAMENTE NO DEBUG
        use_reloader=False,  # ASSOLUTAMENTE NO RELOAD
        threaded=True
    )


# Questo blocco NON verrà eseguito quando importi il modulo
# Serve solo se esegui direttamente python api.py
if __name__ == '__main__':
    run_app()