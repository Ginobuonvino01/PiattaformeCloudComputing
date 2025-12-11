# Crea una versione pulita del file
cat > / home / salvatore / progetto / forecasting_plugin / api.py << 'EOF'
from flask import Flask, jsonify, request
from datetime import datetime
from .collector import collector
from .predictor import ResourcePredictor
import numpy as np

app = Flask(__name__)

# Avvia il collector
collector.start_collection()


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    current = collector.get_current_metrics()

    return jsonify({
        'status': 'healthy',
        'service': 'openstack-forecasting-plugin',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'openstack_connected': collector.conn is not None,
        'metrics': {
            'cpu': current['cpu']['value'] if 'cpu' in current else 0,
            'ram': current['ram']['value'] if 'ram' in current else 0,
            'storage': current['storage']['value'] if 'storage' in current else 0
        },
        'metrics_collected': {
            'cpu': len(collector.metrics_history.get('cpu', [])),
            'ram': len(collector.metrics_history.get('ram', [])),
            'storage': len(collector.metrics_history.get('storage', []))
        }
    })


@app.route('/api/v1/forecast/cpu', methods=['GET'])
def forecast_cpu():
    try:
        hours = request.args.get('hours', default=24, type=int)
        history = collector.get_metrics_history()
        values = [m['value'] for m in history.get('cpu', [])[-168:]]

        predictor = ResourcePredictor()
        forecast = predictor.simple_linear_regression(values, hours)

        return jsonify({
            'metric': 'cpu_usage_percent',
            'forecast_hours': hours,
            'predictions': forecast,
            'current_value': values[-1] if values else 0,
            'data_source': 'OpenStack' if collector.conn else 'Mock',
            'trend': 'increasing' if forecast[-1] > forecast[0] else 'decreasing' if forecast[-1] < forecast[
                0] else 'stable',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/forecast/ram', methods=['GET'])
def forecast_ram():
    try:
        hours = request.args.get('hours', default=24, type=int)
        history = collector.get_metrics_history()
        values = [m['value'] for m in history.get('ram', [])[-168:]]

        predictor = ResourcePredictor()
        forecast = predictor.simple_linear_regression(values, hours)

        return jsonify({
            'metric': 'ram_usage_percent',
            'forecast_hours': hours,
            'predictions': forecast,
            'current_value': values[-1] if values else 0,
            'data_source': 'OpenStack' if collector.conn else 'Mock',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/alerts', methods=['GET'])
def get_alerts():
    alerts = []
    current = collector.get_current_metrics()

    # Alert CPU
    if 'cpu' in current:
        cpu_val = current['cpu']['value']
        if cpu_val > 85:
            alerts.append({
                'severity': 'CRITICAL',
                'resource': 'CPU',
                'message': f'Critical CPU usage: {cpu_val:.1f}%',
                'value': cpu_val,
                'threshold': 85
            })
        elif cpu_val > 70:
            alerts.append({
                'severity': 'WARNING',
                'resource': 'CPU',
                'message': f'High CPU usage: {cpu_val:.1f}%',
                'value': cpu_val,
                'threshold': 70
            })

    # Alert RAM
    if 'ram' in current:
        ram_val = current['ram']['value']
        if ram_val > 90:
            alerts.append({
                'severity': 'CRITICAL',
                'resource': 'RAM',
                'message': f'Critical RAM usage: {ram_val:.1f}%',
                'value': ram_val,
                'threshold': 90
            })
        elif ram_val > 75:
            alerts.append({
                'severity': 'WARNING',
                'resource': 'RAM',
                'message': f'High RAM usage: {ram_val:.1f}%',
                'value': ram_val,
                'threshold': 75
            })

    return jsonify({
        'alerts': alerts,
        'count': len(alerts),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/v1/metrics/current', methods=['GET'])
def get_current_metrics():
    current = collector.get_current_metrics()

    return jsonify({
        'cpu_percent': current.get('cpu', {}).get('value', 0) if current.get('cpu') else 0,
        'ram_percent': current.get('ram', {}).get('value', 0) if current.get('ram') else 0,
        'storage_gb': current.get('storage', {}).get('value', 0) if current.get('storage') else 0,
        'data_source_cpu': current.get('cpu', {}).get('source', 'none') if current.get('cpu') else 'none',
        'data_source_ram': current.get('ram', {}).get('source', 'none') if current.get('ram') else 'none',
        'data_source_storage': current.get('storage', {}).get('source', 'none') if current.get('storage') else 'none',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/v1/metrics/history', methods=['GET'])
def get_history():
    limit = request.args.get('limit', default=100, type=int)
    limit = min(max(1, limit), 1000)

    history = collector.get_metrics_history()
    return jsonify({
        'cpu': history.get('cpu', [])[-limit:],
        'ram': history.get('ram', [])[-limit:],
        'storage': history.get('storage', [])[-limit:],
        'limit': limit,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/v1/openstack/info', methods=['GET'])
def openstack_info():
    info = collector.get_openstack_info()
    info['timestamp'] = datetime.now().isoformat()
    return jsonify(info)


if __name__ == '__main__':
    print("=" * 60)
    print("OpenStack AI Resource Forecasting Service")
    print(f"Version: 2.0.0")
    print(f"Data source: {'OpenStack' if collector.conn else 'Mock data'}")
    print(f"Running on: http://0.0.0.0:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF