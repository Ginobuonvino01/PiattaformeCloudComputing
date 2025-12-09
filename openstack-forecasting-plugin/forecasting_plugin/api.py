from flask import Flask, jsonify, request
import numpy as np
import threading
import time
from datetime import datetime
from predictor import ResourcePredictor

app = Flask(__name__)

# Database in-memory per le metriche
metrics_history = {
    'cpu': [],
    'ram': [],
    'storage': []
}


# Simulazione di dati se non ci sono dati reali
def generate_mock_data():
    """Genera dati mock per testing"""
    import random
    from datetime import datetime, timedelta

    if len(metrics_history['cpu']) == 0:
        # Crea 7 giorni di dati mock
        base_time = datetime.now() - timedelta(days=7)
        for i in range(168):  # 7 giorni * 24 ore
            timestamp = base_time + timedelta(hours=i)
            metrics_history['cpu'].append({
                'timestamp': timestamp.isoformat(),
                'value': 30 + random.uniform(-10, 10) + (i % 24) * 2
            })
            metrics_history['ram'].append({
                'timestamp': timestamp.isoformat(),
                'value': 40 + random.uniform(-15, 15) + (i % 24) * 1.5
            })
            metrics_history['storage'].append({
                'timestamp': timestamp.isoformat(),
                'value': 500 + i * 0.5
            })


# Genera dati mock all'avvio (per testing)
generate_mock_data()


# Endpoint API
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Endpoint di health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'openstack-forecasting-plugin',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'metrics_collected': {
            'cpu': len(metrics_history['cpu']),
            'ram': len(metrics_history['ram']),
            'storage': len(metrics_history['storage'])
        }
    })


@app.route('/api/v1/forecast/cpu', methods=['GET'])
def forecast_cpu():
    """Endpoint per forecasting CPU"""
    try:
        hours = request.args.get('hours', default=24, type=int)

        if not metrics_history['cpu']:
            return jsonify({
                'error': 'No historical data available',
                'suggestion': 'Collect some data first or wait for collection interval'
            }), 400

        # Estrai gli ultimi valori (max ultima settimana)
        values = [m['value'] for m in metrics_history['cpu'][-168:]]

        # Crea predictor e fai forecasting
        predictor = ResourcePredictor()
        forecast = predictor.simple_linear_regression(values, forecast_hours=hours)

        if forecast is None:
            return jsonify({
                'error': 'Not enough data for forecasting',
                'minimum_required': 2,
                'available': len(values)
            }), 400

        return jsonify({
            'metric': 'cpu_usage_percent',
            'historical_count': len(values),
            'forecast_hours': hours,
            'predictions': forecast,
            'current_value': values[-1] if values else 0,
            'trend': 'increasing' if forecast[-1] > forecast[0] else 'decreasing',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/api/v1/forecast/ram', methods=['GET'])
def forecast_ram():
    """Endpoint per forecasting RAM"""
    try:
        hours = request.args.get('hours', default=24, type=int)

        if not metrics_history['ram']:
            return jsonify({
                'error': 'No historical data available'
            }), 400

        values = [m['value'] for m in metrics_history['ram'][-168:]]

        predictor = ResourcePredictor()
        forecast = predictor.simple_linear_regression(values, forecast_hours=hours)

        if forecast is None:
            return jsonify({
                'error': 'Not enough data for forecasting'
            }), 400

        return jsonify({
            'metric': 'ram_usage_percent',
            'forecast_hours': hours,
            'predictions': forecast,
            'current_value': values[-1] if values else 0,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/v1/alerts', methods=['GET'])
def get_alerts():
    """Genera alert basati su soglie"""
    alerts = []
    current_time = datetime.now()

    # Alert basati su CPU
    if metrics_history['cpu']:
        current_cpu = metrics_history['cpu'][-1]['value']

        if current_cpu > 85:
            alerts.append({
                'severity': 'critical',
                'resource': 'cpu',
                'message': f'Critical CPU usage: {current_cpu:.1f}%',
                'value': current_cpu,
                'threshold': 85,
                'timestamp': current_time.isoformat()
            })
        elif current_cpu > 70:
            alerts.append({
                'severity': 'warning',
                'resource': 'cpu',
                'message': f'High CPU usage: {current_cpu:.1f}%',
                'value': current_cpu,
                'threshold': 70,
                'timestamp': current_time.isoformat()
            })

    # Alert basati su RAM
    if metrics_history['ram']:
        current_ram = metrics_history['ram'][-1]['value']

        if current_ram > 90:
            alerts.append({
                'severity': 'critical',
                'resource': 'ram',
                'message': f'Critical RAM usage: {current_ram:.1f}%',
                'value': current_ram,
                'threshold': 90,
                'timestamp': current_time.isoformat()
            })
        elif current_ram > 75:
            alerts.append({
                'severity': 'warning',
                'resource': 'ram',
                'message': f'High RAM usage: {current_ram:.1f}%',
                'value': current_ram,
                'threshold': 75,
                'timestamp': current_time.isoformat()
            })

    return jsonify({
        'alerts': alerts,
        'count': len(alerts),
        'timestamp': current_time.isoformat()
    })


@app.route('/api/v1/metrics/history', methods=['GET'])
def get_history():
    """Restituisce lo storico delle metriche"""
    limit = request.args.get('limit', default=100, type=int)

    return jsonify({
        'cpu': metrics_history['cpu'][-limit:],
        'ram': metrics_history['ram'][-limit:],
        'storage': metrics_history['storage'][-limit:],
        'limit': limit,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/v1/metrics/current', methods=['GET'])
def get_current_metrics():
    """Restituisce le metriche correnti"""
    current_cpu = metrics_history['cpu'][-1]['value'] if metrics_history['cpu'] else 0
    current_ram = metrics_history['ram'][-1]['value'] if metrics_history['ram'] else 0
    current_storage = metrics_history['storage'][-1]['value'] if metrics_history['storage'] else 0

    return jsonify({
        'cpu_percent': current_cpu,
        'ram_percent': current_ram,
        'storage_gb': current_storage,
        'timestamp': datetime.now().isoformat()
    })


# Avvia il server se eseguito direttamente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)